"""Tokens por captura, retenção de 24h e remoção dos arquivos privados."""
import secrets
from datetime import datetime,timezone,timedelta
from pathlib import Path
from app.database.database import conectar
ROOT=Path(__file__).resolve().parents[2]

def register_token(session_id):
    token=secrets.token_urlsafe(32)
    with conectar() as conn,conn.cursor() as cur:
        cur.execute('UPDATE sessoes_provador SET access_token=%s,expires_at=%s WHERE id=%s',(token,datetime.now(timezone.utc)+timedelta(hours=24),session_id))
    return token

def authorize(session_id,token):
    with conectar() as conn,conn.cursor() as cur:
        cur.execute('SELECT access_token,expires_at FROM sessoes_provador WHERE id=%s',(session_id,));row=cur.fetchone()
    return bool(row and row[0] and secrets.compare_digest(row[0],token or '') and row[1] and row[1]>datetime.now(timezone.utc))

def delete_capture(session_id):
    with conectar() as conn,conn.cursor() as cur:
        cur.execute('SELECT caminho_arquivo,caminho_normalizado FROM sessoes_provador WHERE id=%s',(session_id,));row=cur.fetchone()
        if not row:return
        for name in row:
            if not name:continue
            file=(ROOT/name).resolve()
            if file.is_relative_to((ROOT/'uploads'/'provador').resolve()):file.unlink(missing_ok=True)
        cur.execute('DELETE FROM sessoes_provador WHERE id=%s',(session_id,))

def purge_expired():
    with conectar() as conn,conn.cursor() as cur:
        cur.execute("SELECT id FROM sessoes_provador WHERE expires_at<=NOW() OR (expires_at IS NULL AND criado_em<NOW()-INTERVAL '24 hours')");ids=[row[0] for row in cur.fetchall()]
    for session_id in ids:delete_capture(session_id)
    return len(ids)
