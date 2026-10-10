# VesteIA 2.0 — provador com IA (MVP)

O provador agora funciona **sem PostgreSQL**: envie sua foto e a da peça, aprove o avatar base, vista as peças e compare tamanhos.
Detalhes técnicos, provedores de IA, custos e deploy: `docs/PROVADOR_2_0.md`. Testes e limitações: `docs/RELATORIO_TESTES_2_0.md`.

## 1. Aplicar sobre a instalação atual (Windows / PowerShell)

Mantenha a pasta antiga como backup. Extraia este ZIP em uma pasta **nova** (ex.: `C:\Projetos\VesteIA-2.0`).

```powershell
# Ajuste os dois caminhos:
$antigo = "C:\Projetos\VesteIA_1_5_8_CatVTON_Completo\vesteia"
$novo   = "C:\Projetos\VesteIA-2.0\vesteia"

# (Opcional) reaproveitar o ambiente Python já instalado, para não baixar tudo de novo:
Copy-Item "$antigo\backend\.venv312" "$novo\backend\.venv312" -Recurse

# Criar a configuração a partir do modelo (sem segredos):
Copy-Item "$novo\backend\.env.example" "$novo\backend\.env"
notepad "$novo\backend\.env"
```

No `.env` novo **não** é preciso copiar dados do banco. Se quiser manter algo do `.env` antigo (ex.: `TRYON_*` do CatVTON),
copie só essas linhas — nunca envie o `.env` para ninguém.

## 2. Iniciar (dois terminais)

Opção rápida: dois cliques em `INICIAR_BACKEND.bat` e depois em `INICIAR_FRONTEND.bat`.

Ou no PowerShell, a partir da pasta `vesteia`:

```powershell
# Terminal 1 — backend (porta 8000)
cd backend
py -3.12 -m venv .venv312            # só na primeira vez (pule se copiou o .venv312)
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
.\.venv312\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
# Terminal 2 — frontend (porta 5173)
cd frontend
npm install                          # só na primeira vez
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

Abra **http://127.0.0.1:5173**. Teste rápido do backend: `Invoke-RestMethod http://127.0.0.1:8000/health`
deve mostrar `database_enabled = False`.

## 3. Modos de IA (no `backend/.env`; reinicie o backend após mudar)

| Objetivo | AVATAR_PROVIDER | TRYON_PROVIDER | Custo |
|---|---|---|---|
| Testar o fluxo sem custo (padrão) | `photo` ou `mock` | `mock` | nenhum — imagens carimbadas "SIMULAÇÃO" |
| CatVTON local (como na 1.5.8) | `photo` | `catvton` + `TRYON_ENABLED=true` | nenhum (usa sua GPU) |
| Qualidade das referências | `openai` | `openai` | cobrado pela OpenAI por geração |

`photo` usa a sua foto de corpo inteiro como avatar base (sem IA); para selfie ou meio corpo é preciso um gerador (`openai` ou `mock`).
A assinatura do ChatGPT ou do Claude **não** inclui créditos de API. Siga a seção "Teste controlado com a OpenAI" em `docs/PROVADOR_2_0.md`
antes de ativar `AI_PAID_ENABLED=true`.

## 4. Verificar

```powershell
cd frontend
npm run build                        # build de produção (gera frontend\dist)
npm run lint
# Teste de ponta a ponta com respostas simuladas (backend com AVATAR_PROVIDER=mock e TRYON_PROVIDER=mock, frontend ligado):
npx playwright install chromium      # só na primeira vez
$env:VESTEIA_URL = "http://127.0.0.1:5173"; npm run test:studio
```

```powershell
cd backend
.\.venv312\Scripts\python.exe -m pip install -r requirements-dev.txt   # pytest (só na primeira vez)
.\.venv312\Scripts\python.exe -m pytest tests\test_studio.py
```

## Banco de dados legado (opcional)

Para caber no limite de envio, imagens e o modelo de pose usados **só** pelo modo legado vieram em
`VesteIA_2_0_complemento_legado.zip` (iguais aos da 1.5.8). Extraia-o na mesma pasta pai, por cima do projeto novo,
apenas se for ligar `DATABASE_ENABLED=true`. O histórico Git (branches `original` e `mvp-provador`) está em
`VesteIA_2_0_historico_git.bundle`: `git clone VesteIA_2_0_historico_git.bundle vesteia-git`.

O catálogo antigo, perfis e o provador 2D antigo continuam no código, mas só carregam com `DATABASE_ENABLED=true`
e `pip install -r requirements-legacy.txt`. A interface nova não usa o catálogo. Para remover produtos de demonstração do banco
com backup, veja `backend/scripts/limpeza_catalogo/LEIA.md` (nada é executado automaticamente).
