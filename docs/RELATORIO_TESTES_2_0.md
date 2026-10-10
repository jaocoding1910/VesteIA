# Relatório de testes — VesteIA 2.0 (10/10/2026)

Todos os testes usaram **respostas simuladas** (provedor `mock`) ou um **servidor falso** no lugar da OpenAI.
**Nenhuma chamada paga foi feita e a qualidade real da IA não foi validada.**

## Backend — `backend/tests/test_studio.py` (19 testes, todos passando)
Executados com Python 3.13 e as mesmas versões de FastAPI/Starlette/Pydantic do seu `.venv312`.

* Inicialização sem PostgreSQL (`database_enabled=false`), sem rota de catálogo (`/mvp/catalogo` → 404).
* Sessão obrigatória; origem não autorizada recusada.
* Upload: texto disfarçado de JPG (415), GIF (415), imagem pequena (422), WEBP aceito, orientação EXIF respeitada.
* Avatar: sem consentimento (422), contagem divergente (409), `request_id` repetido (409), regiões estimadas sinalizadas;
  modo `photo` exige corpo inteiro e devolve 1024×1536 sem distorção, com 0 gerações.
* Prova: camiseta + calça na mesma chamada; conflitos de região recusados; trava de sessão bloqueia geração paralela.
* Tamanhos: falta de medidas recusada; contagem confirmada; prévias diferentes por medida; medidas iguais marcadas como repetidas;
  CatVTON recusa prévias por tamanho com mensagem.
* Limites: limite de sessão; contadores relidos do SQLite após "reinício"; limite diário pago.
* OpenAI (servidor falso): não habilita sem chave **e** `AI_PAID_ENABLED`; envia `model=gpt-image-2`, `size=1024x1536`, sem
  `input_fidelity`, imagens como data URL; base + 2 peças em uma única chamada; erro 500 → exatamente 1 requisição (sem repetição);
  resposta sem imagem → "inconclusiva"; chave inválida → cota devolvida.
* Funções puras: filtro de logs (base64, `sk-`, Bearer), leitura de folga dependente de medidas, regras do look.

## Frontend
* ESLint do projeto: 0 erros (2 avisos preexistentes em `LegacyProvador.jsx`).
* Empacotamento verificado com **esbuild** (o `vite build` não pôde rodar neste ambiente Linux: o binário nativo do Rolldown
  instalado é o de Windows e não havia acesso ao npm). **Rode `npm run build` no Windows** antes do deploy.
* `frontend/tests/studio-e2e.mjs` (Playwright, Chromium): 36 verificações passando —
  homepage sem banco, vídeo com controles/capa/sem autoplay, exemplos marcados como ilustrativos, nenhuma chamada ao catálogo,
  arquivo inválido recusado, aviso de regiões estimadas, categoria obrigatória, consentimento obrigatório, contagem de gerações,
  clique triplo = 1 chamada, antes/depois, troca de aba sem geração, estado sem medidas, folga com medidas do cliente,
  confirmação com número de gerações (cancelar não gera), look desatualizado sem geração automática, erro de serviço exibido,
  limpar sessão (DELETE + imagens descartadas), sem erros de JavaScript, 390 px sem rolagem horizontal, movimento reduzido,
  serviço indisponível com "Tentar novamente".
* Revisão visual por capturas de tela em 1366 px e 390 px.

## Não testado aqui
* Scripts `.bat`/PowerShell (ambiente Linux) — revisados, não executados.
* CatVTON, avatar local e Google Vertex reais (dependem do seu computador/credenciais).
* OpenAI real (depende de chave, créditos e da sua decisão de custo) — siga o "Teste controlado" em `PROVADOR_2_0.md`.
* Testes antigos de backend (`test_mvp.py` etc.) exigem PostgreSQL e as dependências legadas.
* Fonte Montserrat (Google Fonts) não carregou neste ambiente sem internet; a interface usa a fonte do sistema como alternativa.
