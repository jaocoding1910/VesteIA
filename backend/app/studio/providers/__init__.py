"""Seleção de provedores por variável de ambiente.

AVATAR_PROVIDER: photo (padrão, sem IA) | mock | openai | local
TRYON_PROVIDER:  mock (padrão) | openai | catvton | google-vertex
"""
from __future__ import annotations

from app.config import Settings
from app.studio.providers.base import Capabilities, ProviderError


class _Unavailable:
    def __init__(self, name: str):
        self.name = name

    def capabilities(self) -> Capabilities:
        return Capabilities(id=self.name or "none", label="Não configurado", kind="none", paid=False, ready=False,
                            message=f"Provedor '{self.name}' desconhecido. Revise o backend/.env.")

    def planned_calls(self, request) -> int:
        return 0

    def _fail(self, *_args, **_kwargs):
        raise ProviderError(self.capabilities().message, 503)

    generate_avatar = try_on = size_preview = _fail


def avatar_provider(settings: Settings):
    from app.studio.providers.local import LocalSelfieAvatarProvider, PhotoAvatarProvider
    from app.studio.providers.mock import MockProvider
    from app.studio.providers.openai_images import OpenAIImagesProvider
    return {"photo": PhotoAvatarProvider, "mock": MockProvider, "local": LocalSelfieAvatarProvider,
            "openai": lambda: OpenAIImagesProvider(settings)}.get(settings.avatar_provider, lambda: _Unavailable(settings.avatar_provider))()


def tryon_provider(settings: Settings):
    from app.studio.providers.local import LegacyTryOnProvider
    from app.studio.providers.mock import MockProvider
    from app.studio.providers.openai_images import OpenAIImagesProvider
    name = settings.tryon_provider
    if name in ("catvton", "google-vertex"):
        return LegacyTryOnProvider(name)
    return {"mock": MockProvider, "openai": lambda: OpenAIImagesProvider(settings)}.get(name, lambda: _Unavailable(name))()
