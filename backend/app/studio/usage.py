"""Limite de chamadas persistente (SQLite), sobrevive a reinicializações.

Guarda somente contadores e eventos sem imagem: data, provedor, tipo, quantidade e status.
A reserva acontece ANTES da chamada; se a requisição nem chegou ao serviço, é devolvida.
"""
from __future__ import annotations

import hashlib
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app.config import Settings

_LOCK = threading.Lock()


class LimitExceeded(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def hash_key(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:24]


class UsageLedger:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS counters (
                    day TEXT NOT NULL, scope TEXT NOT NULL, key TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (day, scope, key));
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, provider TEXT NOT NULL,
                    kind TEXT NOT NULL, calls INTEGER NOT NULL, status TEXT NOT NULL, session_hash TEXT);
            """)

    @contextmanager
    def _conn(self):
        db = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        try:
            yield db
        finally:
            db.close()

    def _get(self, db, day: str, scope: str, key: str) -> int:
        row = db.execute("SELECT count FROM counters WHERE day=? AND scope=? AND key=?", (day, scope, key)).fetchone()
        return int(row[0]) if row else 0

    def _add(self, db, day: str, scope: str, key: str, amount: int) -> None:
        db.execute("""INSERT INTO counters(day, scope, key, count) VALUES (?, ?, ?, ?)
                      ON CONFLICT(day, scope, key) DO UPDATE SET count = MAX(0, count + excluded.count)""",
                   (day, scope, key, amount))

    def snapshot(self, settings: Settings, session_id: str | None = None) -> dict:
        day = _today()
        with _LOCK, self._conn() as db:
            paid_day = self._get(db, day, "paid", "global")
            paid_total = self._get(db, "total", "paid", "global")
            local_day = self._get(db, day, "local", "global")
            session = self._get(db, "session", "session", hash_key(session_id)) if session_id else 0
        return {
            "pagas_hoje": paid_day, "limite_pagas_dia": settings.daily_limit_paid,
            "pagas_total": paid_total, "limite_pagas_total": settings.total_limit_paid,
            "locais_hoje": local_day, "limite_locais_dia": settings.daily_limit_local,
            "sessao": session, "limite_sessao": settings.session_limit,
        }

    def remaining(self, settings: Settings, *, paid: bool, session_id: str) -> int:
        snap = self.snapshot(settings, session_id)
        values = [snap["limite_sessao"] - snap["sessao"]]
        if paid:
            values += [snap["limite_pagas_dia"] - snap["pagas_hoje"], snap["limite_pagas_total"] - snap["pagas_total"]]
        else:
            values.append(snap["limite_locais_dia"] - snap["locais_hoje"])
        return max(0, min(values))

    def reserve(self, settings: Settings, *, paid: bool, session_id: str, calls: int) -> None:
        if calls <= 0:
            return
        day, skey = _today(), hash_key(session_id)
        with _LOCK, self._conn() as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                session_used = self._get(db, "session", "session", skey)
                if session_used + calls > settings.session_limit:
                    raise LimitExceeded(
                        f"Limite desta sessão atingido ({settings.session_limit} gerações). Limpe a sessão ou tente mais tarde.")
                if paid:
                    if self._get(db, day, "paid", "global") + calls > settings.daily_limit_paid:
                        raise LimitExceeded(f"Limite diário de gerações pagas atingido ({settings.daily_limit_paid}).")
                    if self._get(db, "total", "paid", "global") + calls > settings.total_limit_paid:
                        raise LimitExceeded(f"Limite total de gerações pagas atingido ({settings.total_limit_paid}). Ajuste AI_TOTAL_LIMIT_PAID conscientemente.")
                    self._add(db, day, "paid", "global", calls)
                    self._add(db, "total", "paid", "global", calls)
                else:
                    if self._get(db, day, "local", "global") + calls > settings.daily_limit_local:
                        raise LimitExceeded(f"Limite diário de gerações locais/simuladas atingido ({settings.daily_limit_local}).")
                    self._add(db, day, "local", "global", calls)
                self._add(db, "session", "session", skey, calls)
                db.execute("COMMIT")
            except BaseException:
                db.execute("ROLLBACK")
                raise

    def release(self, *, paid: bool, session_id: str, calls: int) -> None:
        """Devolve chamadas que não chegaram a ser enviadas ao provedor."""
        if calls <= 0:
            return
        day, skey = _today(), hash_key(session_id)
        with _LOCK, self._conn() as db:
            if paid:
                self._add(db, day, "paid", "global", -calls)
                self._add(db, "total", "paid", "global", -calls)
            else:
                self._add(db, day, "local", "global", -calls)
            self._add(db, "session", "session", skey, -calls)

    def record(self, *, provider: str, kind: str, calls: int, status: str, session_id: str | None) -> None:
        with _LOCK, self._conn() as db:
            db.execute("INSERT INTO events(at, provider, kind, calls, status, session_hash) VALUES (?, ?, ?, ?, ?, ?)",
                       (datetime.now(timezone.utc).isoformat(timespec="seconds"), provider, kind, calls, status,
                        hash_key(session_id) if session_id else None))

    def sessions_from_ip(self, ip: str) -> int:
        with _LOCK, self._conn() as db:
            return self._get(db, _today(), "session_ip", hash_key(ip))

    def count_session_from_ip(self, ip: str) -> None:
        with _LOCK, self._conn() as db:
            self._add(db, _today(), "session_ip", hash_key(ip), 1)


_LEDGERS: dict[str, UsageLedger] = {}


def get_ledger(settings: Settings) -> UsageLedger:
    key = str(settings.usage_db_path)
    if key not in _LEDGERS:
        _LEDGERS[key] = UsageLedger(settings.usage_db_path)
    return _LEDGERS[key]
