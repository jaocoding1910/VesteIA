"""Ponto de extensão para créditos financiados pela loja (NÃO implementado nesta etapa).

Hoje a única política é o limite local (usage.py). No futuro, uma loja parceira
poderá financiar as gerações de seus clientes. Para isso será necessário, no mínimo:
- cadastro de lojas com chave própria e saldo de créditos (banco de dados);
- autenticação da loja/cliente (o token de sessão anônimo não basta);
- reserva e débito atômicos por geração, com conciliação contra a fatura do provedor;
- regras anti-abuso por cliente e por loja; trilha de auditoria;
- termos de uso e privacidade da loja; webhooks de confirmação de compra (fora do escopo).
Não há cobrança real, check-in, cashback ou confirmação de compra neste MVP.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class CreditDecision:
    allowed: bool
    reason: str = ""
    sponsor: str | None = None  # futura loja financiadora


class CreditPolicy(Protocol):
    def authorize(self, *, session_id: str, provider: str, calls: int, store_id: str | None) -> CreditDecision: ...
    def settle(self, *, session_id: str, provider: str, calls: int, status: str, store_id: str | None) -> None: ...


class NoSponsorPolicy:
    """Padrão: nenhuma loja financia; vale apenas o limite local configurado no .env."""

    def authorize(self, *, session_id: str, provider: str, calls: int, store_id: str | None) -> CreditDecision:
        if store_id:
            return CreditDecision(False, "Créditos de loja ainda não estão disponíveis nesta versão.")
        return CreditDecision(True)

    def settle(self, *, session_id: str, provider: str, calls: int, status: str, store_id: str | None) -> None:
        return None


POLICY: CreditPolicy = NoSponsorPolicy()
