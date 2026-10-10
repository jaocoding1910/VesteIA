# VesteIA 2.0 — provador: arquitetura, IA, custos e deploy

## Visão geral

```
frontend (React/Vite)                      backend (FastAPI)                   provedores
 Home  ── #provador ──► StudioPage  ──►  /api/studio/*  ──► interface ─┬─ mock (simulado, sem custo)
  6 etapas, estado só em memória          sessão anônima      AvatarProvider   ├─ photo (foto como avatar, sem IA)
  Antes e depois | Comparar tamanhos      limites SQLite      TryOnProvider    ├─ catvton (local, 1.5.8)
                                          sem PostgreSQL                       ├─ google-vertex (1.5.8)
                                                                               ├─ local (avatar por selfie, 1.5.8)
                                                                               └─ openai (Images API, gpt-image-2)
```

* `DATABASE_ENABLED=false` (padrão): só o provador é carregado. Nada consulta, cria ou preenche o catálogo.
* `DATABASE_ENABLED=true`: carrega também as rotas legadas (catálogo, perfis, provador 2D, `/mvp/ia/*`), como na 1.5.8.

### Rotas do provador

| Método | Rota | Custo | O que faz |
|---|---|---|---|
| GET | `/api/studio/status` | — | provedores, capacidades, limites, categorias |
| POST | `/api/studio/session` | — | cria sessão anônima (limitada por IP/dia; código opcional `STUDIO_ACCESS_CODE`) |
| DELETE | `/api/studio/session` | — | encerra a sessão ("Limpar sessão") |
| POST | `/api/studio/photo/check` | — | valida formato, tamanho, orientação; dá avisos de qualidade |
| POST | `/api/studio/avatar` | 0–1 geração | avatar base a partir da foto |
| POST | `/api/studio/tryon` | 1 (openai/mock) ou 1 por peça (CatVTON/Vertex) | veste as peças no avatar aprovado |
| POST | `/api/studio/size-previews` | 1 por tamanho | prévias ilustrativas por medidas (só provedores que aceitam medidas) |
| GET | `/api/studio/usage` | — | uso da sessão e do dia |

Toda geração exige: token de sessão, origem autorizada (CORS), consentimento, `request_id` único (impede clique duplicado),
`expected_calls` igual ao número calculado pelo servidor (garante que a pessoa viu a contagem) e cota disponível.
Há uma trava por sessão e um limite global de gerações simultâneas (`AI_MAX_CONCURRENT`).

## Fluxo do provador

1. **Foto** — JPEG/PNG/WEBP, validada no navegador e no servidor (assinatura do arquivo, tamanho, resolução, EXIF). A pessoa
   informa o enquadramento (rosto, meio corpo, corpo inteiro) e se está sem camiseta. A foto é exibida contida, nunca esticada.
2. **Peças** — até `AI_MAX_GARMENTS` imagens.
3. **Categoria e tamanho** — categoria obrigatória; tamanhos, tamanho escolhido e medidas da peça opcionais; medidas do cliente opcionais.
4. **Avatar base** — geração explícita, comparação "Sua foto × Avatar base", aprovação obrigatória. Regiões estimadas são avisadas.
5. **Vestir** — peças do look (uma por região: cima, sobreposição, baixo, peça inteira). Sempre parte do avatar aprovado,
   para não acumular alterações entre gerações.
6. **Comparar** — abas **Antes e depois** (montar o look: vestir, substituir, remover; reprocessar só por clique) e
   **Comparar tamanhos** (tabela por medidas + prévias visuais opcionais com confirmação do número de gerações).

### Comparação de tamanhos — regras

* Só usa medidas informadas. Sem medidas, mostra a falta e permite preencher; não estima centímetros pela imagem.
* Folga = (medida plana × 2) − circunferência do corpo. As faixas (justa/regular/folgada…) são aproximações e dependem de tecido e modelagem.
  O mesmo rótulo pode ser justo para uma pessoa e amplo para outra (há teste automatizado para isso).
* Prévias visuais por tamanho só existem em provedores que recebem medidas (`openai`, `mock`). CatVTON e Vertex não recebem medidas:
  a interface informa e entrega apenas a comparação de medidas, em vez de repetir a mesma imagem.
* Se duas prévias saírem praticamente iguais, o backend marca `repeated_of` e a interface avisa para não usar como diferença.
* Mesmo com a OpenAI, as prévias são **ilustrativas** (o modelo segue o texto com as medidas, sem física de tecido).

## Avaliação dos provedores para o seu hardware (8 GB RAM, GPU 6 GB)

| Provedor | Qualidade esperada | Requisitos | Licença/custo | Situação |
|---|---|---|---|---|
| `mock` | nenhuma (colagem) | nenhum | — | testes do fluxo |
| `photo` | a própria foto | foto de corpo inteiro | — | avatar sem IA |
| CatVTON local | moderada; na 1.5.8 roda a 384×512 para caber na GPU | GPU ~6 GB, já instalado por você | pesos com licença não comercial (CC BY-NC-SA, verifique antes de uso comercial) | preservado; veste 1 peça por chamada; não gera avatar nem tamanhos |
| Avatar local (IP-Adapter) | experimental; tende a usar corpo de modelo | downloads de vários GB, 8 GB RAM é o limite | verifique licenças dos modelos | preservado, mas o resultado é **descartado** se colar o rosto em corpo fixo |
| Google Vertex Virtual Try-On | boa para roupa | conta Google Cloud com faturamento | pago por imagem | preservado (1 peça por chamada) |
| OpenAI `gpt-image-2` | a mais próxima das referências (identidade + várias peças por chamada) | só internet; chave de API com créditos | pago por geração | **novo**, recomendado para qualidade |

Nenhum modelo foi treinado nem baixado nesta etapa. Treinar do zero não é viável nesse hardware.

## OpenAI Images API — o que foi confirmado (documentação oficial, out/2026)

* Modelo `gpt-image-2` (snapshot `gpt-image-2-2026-04-21`) aceito em `POST /v1/images/edits`, que recebe **até 16 imagens de referência**.
* Para `gpt-image-2`, o parâmetro `input_fidelity` deve ser **omitido**.
* `size` aceita `WIDTHxHEIGHT` com lados múltiplos de 16 (usamos `1024x1536`, retrato 2:3). `quality`: `low`, `medium`, `high`, `auto`.
* A resposta traz a imagem em `data[0].b64_json`. Pode ser necessária a **verificação da organização** na OpenAI para usar modelos GPT Image.
* A referência atual descreve o corpo em JSON (`images: [{image_url: "data:..."}]`). O formato clássico multipart (`image[]`) também foi
  implementado; escolha com `OPENAI_EDITS_TRANSPORT` caso o teste controlado retorne erro 400 de formato.
* Preço: consulte https://openai.com/api/pricing e a calculadora do guia de imagens. Na consulta, a página listava preços por milhão
  de tokens (texto/imagem de entrada e imagem de saída), sem valor fixo por imagem — o custo varia com qualidade, tamanho e nº de referências.
* A assinatura do ChatGPT (ou do Claude) **não** dá créditos de API. Nenhuma automação de site de chatbot é usada.

Fontes: https://developers.openai.com/api/docs/models/gpt-image-2 ·
https://developers.openai.com/api/reference/resources/images/methods/edit ·
https://developers.openai.com/api/docs/guides/image-generation · https://developers.openai.com/api/docs/pricing

### Teste controlado com a OpenAI (faça somente quando decidir)

1. Em platform.openai.com: crie uma chave de API, adicione créditos e defina um **limite de gasto mensal baixo**. Conclua a verificação da organização se for pedida.
2. No `backend/.env`:
   ```
   OPENAI_API_KEY=sk-...            # nunca no frontend, nunca no Git
   AI_PAID_ENABLED=true
   AVATAR_PROVIDER=openai
   TRYON_PROVIDER=openai
   OPENAI_IMAGE_QUALITY=low         # primeiro teste mais barato
   AI_DAILY_LIMIT_PAID=3
   AI_TOTAL_LIMIT_PAID=3            # trava total: no máximo 3 gerações pagas
   ```
3. Reinicie o backend e confira em `http://127.0.0.1:8000/api/studio/status` que `avatar.ready` e `tryon.ready` são `true`.
4. No provador: uma foto de corpo inteiro e uma camiseta. Gere o avatar (1 chamada) e a prova (1 chamada). Avalie identidade,
   roupa (cor, gola, mangas, estampa) e ausência de "adesivo".
5. Se der erro 400 de formato, troque `OPENAI_EDITS_TRANSPORT=multipart` e repita (a cota restante continua valendo).
6. Depois de aprovar a qualidade, suba `OPENAI_IMAGE_QUALITY` e os limites conscientemente. Volte `AI_PAID_ENABLED=false` para desligar.

## Custo e controle

* Geração só por clique; o botão mostra quantas gerações serão solicitadas e quantas restam. Prévias por tamanho pedem confirmação.
* Trocar de aba, de tamanho ou de peça **não** gera nada; o look fica marcado como "desatualizado" até um novo clique.
* Sem novas tentativas automáticas (nem no cliente HTTP). Falhas mostram se a tentativa foi contabilizada; respostas sem imagem
  são tratadas como "inconclusivas".
* Limites persistentes em `backend/data/usage.sqlite3` (só contadores e eventos, sem imagens): `AI_DAILY_LIMIT_PAID`,
  `AI_TOTAL_LIMIT_PAID`, `AI_DAILY_LIMIT_LOCAL`, `AI_SESSION_LIMIT`, `AI_SESSIONS_PER_IP_DAILY`.
  A cota é reservada antes da chamada e só devolvida quando é certo que nada chegou ao provedor.

### Créditos financiados pela loja (futuro)

Ponto de extensão em `backend/app/studio/credits.py` (`CreditPolicy.authorize/settle`). Não há cobrança real, check-in, cashback
nem confirmação de compra. Para implementar será preciso: cadastro de lojas e saldo (banco), autenticação de loja/cliente,
débito atômico por geração com conciliação com a fatura do provedor, antifraude, auditoria, termos e privacidade da loja e
integração com a confirmação de compra.

## Privacidade e segurança

* Chaves só no backend (`.env`, fora do Git). O frontend nunca recebe segredos.
* Consentimento antes de qualquer processamento; o texto muda conforme o provedor (local, externo com custo, simulado).
* Validação de tipo real do arquivo, tamanho (`MAX_UPLOAD_MB`), resolução e limite do corpo da requisição.
* Logs com filtro que remove base64, data URLs, chaves `sk-...` e tokens. Corpos de requisição não são registrados.
* Nenhuma foto é gravada em disco ou banco; respostas com `Cache-Control: no-store`. "Limpar sessão" descarta tudo.
* Endpoints de geração exigem sessão, origem autorizada e cota. Para teste público, use `STUDIO_ACCESS_CODE`.

## Deploy futuro (não publicado agora)

1. **Backend**: um serviço Python 3.12 (Render, Railway, Fly.io, VM) com `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   atrás de HTTPS. Variáveis do `.env.example` configuradas no painel do provedor (nunca no repositório).
   `backend/data/` precisa de **disco persistente** para os limites sobreviverem a reinícios.
2. **Frontend**: `npm run build` com `VITE_API_BASE_URL=https://api.seudominio` e publicação de `frontend/dist` em hospedagem estática
   (Netlify, Vercel, Cloudflare Pages). Coloque o domínio do frontend em `CORS_ORIGINS`.
3. Antes de abrir ao público: `STUDIO_ACCESS_CODE`, limites baixos, limite de gasto na OpenAI, política de privacidade revisada
   por um profissional (LGPD: fotos de rosto são dados pessoais; avalie base legal e termos do provedor externo),
   e monitoramento de erros sem registrar imagens.
4. CatVTON/avatar local não servem para deploy em nuvem barata (exigem GPU); em produção, use `openai` ou outro provedor via API.
5. Várias instâncias do backend exigem trocar o SQLite e as sessões em memória por Redis/PostgreSQL (o contrato já está isolado).

## Limitações conhecidas

* A qualidade real da IA **não foi validada**: nenhuma chamada paga foi feita. Os testes usaram respostas simuladas e um servidor falso no lugar da OpenAI.
* Selfie de rosto não permite medir o corpo; o corpo gerado é estimativa.
* Ângulos extremos, roupas largas cobrindo o corpo, baixa luz e várias pessoas na foto podem falhar; a interface orienta, mas não detecta pose
  (o detector MediaPipe antigo continua só no modo legado).
* O provedor pode recusar fotos pelo filtro de segurança, sobretudo sem camiseta; a mensagem é exibida e nada é repetido.
* Prévias por tamanho são ilustrativas, mesmo orientadas por medidas.
