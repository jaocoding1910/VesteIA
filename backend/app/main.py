"""VesteIA — backend.

Modo padrão (DATABASE_ENABLED=false): inicia sem PostgreSQL e expõe apenas o
provador (/api/studio). As rotas legadas de catálogo, perfis e provador 2D só são
carregadas com DATABASE_ENABLED=true; nesse modo nada é criado ou preenchido
automaticamente no catálogo.
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app import logging_safe
from app.config import get_settings
from app.studio.api import http_error_handler, router as studio_router

logging_safe.install()
log = logging.getLogger("vesteia")
settings = get_settings()


@asynccontextmanager
async def lifespan(_app):
    task = None
    if settings.database_enabled:
        from app.services.photo_privacy import purge_expired

        async def cleanup():
            while True:
                try:
                    await asyncio.to_thread(purge_expired)
                except Exception:  # noqa: BLE001
                    log.warning("Limpeza de capturas legadas indisponível; confira banco e migrations.")
                await asyncio.sleep(600)

        task = asyncio.create_task(cleanup())
    log.info("VesteIA iniciado. Banco legado: %s", "ligado" if settings.database_enabled else "desligado")
    yield
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="VesteIA", version="2.0.0", lifespan=lifespan)
app.add_exception_handler(HTTPException, http_error_handler)
app.include_router(studio_router)

STUDIO_BODY_LIMIT = (settings.max_garments + 2) * settings.max_upload_bytes + 1024 * 1024


@app.get("/health")
def health():
    return {"status": "ok", "app": "VesteIA", "database_enabled": settings.database_enabled}


@app.middleware("http")
async def studio_guard(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api/studio") and request.method in ("POST", "PUT", "DELETE"):
        origin = request.headers.get("origin")
        if origin and origin not in settings.cors_origins:
            return JSONResponse({"detail": "Origem não autorizada."}, status_code=403)
        if request.method == "POST":
            try:
                length = int(request.headers.get("content-length", "-1"))
            except ValueError:
                return JSONResponse({"detail": "Tamanho de requisição inválido."}, status_code=400)
            if length < 0:
                return JSONResponse({"detail": "Informe o tamanho da requisição."}, status_code=411)
            if length > STUDIO_BODY_LIMIT:
                return JSONResponse({"detail": "Arquivos acima do limite permitido."}, status_code=413)
    try:
        response = await call_next(request)
    except Exception:  # noqa: BLE001 - não expor detalhes internos
        log.exception("Falha inesperada em %s", path)
        return JSONResponse({"detail": "Não foi possível concluir. Tente novamente."}, status_code=500)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    if path.startswith("/api/studio"):
        response.headers["Cache-Control"] = "no-store"
    return response


if settings.database_enabled:
    # Rotas legadas (exigem PostgreSQL e as dependências de requirements-legacy.txt).
    import re

    from app.api.mvp import router as mvp_router
    from app.api.provador import router as provador_router
    from app.api.routes import router as legacy_router
    from app.api.selfie_api import router as selfie_router
    from app.api.tryon_api import router as virtual_tryon_router
    from app.services.photo_privacy import authorize

    app.include_router(provador_router)
    app.include_router(legacy_router)
    app.include_router(mvp_router)
    app.include_router(virtual_tryon_router)
    app.include_router(selfie_router)

    @app.middleware("http")
    async def private_captures(request: Request, call_next):
        path = request.url.path
        if path == "/provador/sessoes":
            return JSONResponse({"detail": "Listagem de capturas privada desativada no MVP."}, status_code=403)
        match = re.match(r"^/provador/sessoes/(\d+)(?:/|$)", path)
        if match and request.method != "OPTIONS":
            try:
                allowed = authorize(int(match[1]), request.headers.get("Authorization", "").removeprefix("Bearer "))
            except Exception:  # noqa: BLE001
                return JSONResponse({"detail": "Banco indisponível. Tente novamente."}, status_code=503)
            if not allowed:
                return JSONResponse({"detail": "Captura expirada ou acesso inválido."}, status_code=403)
        return await call_next(request)

    @app.middleware("http")
    async def limit_ai_upload(request: Request, call_next):
        if request.url.path in ("/mvp/ia/previa", "/mvp/ia/avatar") and request.method == "POST":
            origin = request.headers.get("origin")
            if origin and origin not in settings.cors_origins:
                return JSONResponse({"detail": "Origem não autorizada."}, status_code=403)
            try:
                length = int(request.headers.get("content-length", "0"))
            except ValueError:
                return JSONResponse({"detail": "Tamanho de requisição inválido."}, status_code=400)
            if length <= 0:
                return JSONResponse({"detail": "Informe o tamanho da requisição."}, status_code=411)
            if length > 15 * 1024 * 1024:
                return JSONResponse({"detail": "Envie duas imagens de até 7 MB cada."}, status_code=413)
        return await call_next(request)

# CORS por último = camada mais externa (inclui cabeçalhos também nas respostas de erro).
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)
