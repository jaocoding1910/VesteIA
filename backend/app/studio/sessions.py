"""Sessões anônimas do provador, somente em memória.

Nenhuma foto fica no servidor: o navegador guarda as imagens da sessão e as envia
a cada etapa. A sessão contém apenas token, validade, ids de requisição já usados
(para impedir duplicidade) e uma trava que bloqueia gerações simultâneas.
"""
from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass, field


@dataclass
class StudioSession:
    id: str
    token: str
    expires_at: float
    lock: threading.Lock = field(default_factory=threading.Lock)
    request_ids: set[str] = field(default_factory=set)


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, StudioSession] = {}
        self._guard = threading.Lock()

    def create(self, ttl_minutes: int) -> StudioSession:
        self.purge()
        session = StudioSession(id=secrets.token_urlsafe(12), token=secrets.token_urlsafe(32),
                                expires_at=time.time() + ttl_minutes * 60)
        with self._guard:
            self._sessions[session.token] = session
        return session

    def get(self, token: str | None) -> StudioSession | None:
        if not token:
            return None
        with self._guard:
            session = self._sessions.get(token)
        if not session:
            return None
        if session.expires_at < time.time():
            self.drop(token)
            return None
        return session

    def drop(self, token: str) -> bool:
        with self._guard:
            return self._sessions.pop(token, None) is not None

    def purge(self) -> None:
        now = time.time()
        with self._guard:
            for token in [t for t, s in self._sessions.items() if s.expires_at < now]:
                self._sessions.pop(token, None)

    def clear(self) -> None:
        with self._guard:
            self._sessions.clear()


STORE = SessionStore()
