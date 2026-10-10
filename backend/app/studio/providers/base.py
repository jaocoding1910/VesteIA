"""Contrato comum dos provedores de imagem. Trocar de provedor não muda a API do app."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from PIL import Image


class ProviderError(Exception):
    """Falha de geração.

    sent=True indica que a requisição chegou ao serviço (pode ter havido cobrança);
    nesse caso a chamada continua contabilizada no limite.
    """

    def __init__(self, message: str, status: int = 502, *, sent: bool = False, inconclusive: bool = False):
        super().__init__(message)
        self.message = message
        self.status = status
        self.sent = sent
        self.inconclusive = inconclusive


@dataclass
class Capabilities:
    id: str
    label: str
    kind: str  # "local" | "external" | "simulated" | "none"
    paid: bool
    ready: bool
    message: str
    model: str | None = None
    generates: bool = True  # False = não usa IA (ex.: foto de corpo inteiro como avatar)
    multi_garment: bool = False  # veste várias peças numa única chamada
    size_previews: bool = False  # consegue gerar prévias orientadas por medidas
    accepts_partial_photo: bool = True  # aceita selfie/meio corpo (estima o restante)

    def public(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class GarmentInput:
    image: Image.Image
    category: str
    slot: str
    description: str = ""
    size_label: str | None = None
    measures: dict[str, float] = field(default_factory=dict)


@dataclass
class AvatarRequest:
    photo: Image.Image
    framing: str  # "rosto" | "meio_corpo" | "corpo_inteiro"
    upper_state: str  # "vestido" | "sem_camiseta" | "nao_informado"
    body_reference: str | None = None  # apenas para o gerador local legado


@dataclass
class TryOnRequest:
    base: Image.Image
    garments: list[GarmentInput]


@dataclass
class SizePreviewRequest:
    base: Image.Image
    garment: GarmentInput
    size_label: str
    selected_label: str
    measures: dict[str, float]
    selected_measures: dict[str, float]
    body: dict[str, float]
    description: str


@dataclass
class Generated:
    image: Image.Image
    provider: str
    model: str | None
    simulated: bool
    calls: int
    notes: list[str] = field(default_factory=list)


class AvatarProvider(Protocol):
    def capabilities(self) -> Capabilities: ...
    def planned_calls(self, request: AvatarRequest) -> int: ...
    def generate_avatar(self, request: AvatarRequest) -> Generated: ...


class TryOnProvider(Protocol):
    def capabilities(self) -> Capabilities: ...
    def planned_calls(self, request: TryOnRequest) -> int: ...
    def try_on(self, request: TryOnRequest) -> Generated: ...
    def size_preview(self, request: SizePreviewRequest) -> Generated: ...
