# VesteIA — MVP integrado 1.0

Atualização visual: manequins neutros, roupas por categoria, dimensões por SKU e estampas. Para atualizar uma instalação que já funciona, substitua somente `frontend/src` e copie `frontend/public/assets`; preserve `.env` e banco. Detalhes e limitações em `docs/CORRECAO_AVATAR.md`.

Loja de demonstração com provador pessoal, comparação de tamanhos, perfil, fotografia opcional, favoritos, sacola e look. A composição visual segue a referência enviada: tema escuro, acentos ciano/violeta, ficha de produto à esquerda e cartões de tamanhos no centro.

O FastAPI, PostgreSQL e o pipeline corporal das sprints anteriores foram preservados. A nova experiência está em módulos React; a tela anterior pode ser aberta por **Provador original**, no rodapé.

## O que está integrado

- Loja pesquisável com seis categorias: camiseta, calça, bermuda, saia, vestido e calçado.
- Produtos com variantes, cores, tabela de medidas, grade ordenada pelo catálogo e estoque real do banco.
- Onboarding com apelido, apresentação masculina/feminina, aparência e medidas opcionais.
- Comparação simultânea no desktop; um tamanho em destaque e abas no celular.
- Recomendação por medidas declaradas, com razões e confiança; sugestão legada de baixa confiança quando só há altura/peso.
- Bases naturais artísticas para camiseta preta e representação vetorial dinâmica para personalização, outras categorias e look.
- Fotografia opcional ligada ao detector MediaPipe e ao renderer normalizado existente.
- Favoritos e sacola persistidos no navegador; validação de preço/estoque na API; peças ativáveis no look.
- Capturas privadas com token individual, validação de conteúdo/tamanho/resolução, exclusão e expiração.
- Migrações aditivas, ponte para SKUs anteriores, seed idempotente e importador de catálogo externo.

## Requisitos

- Python **3.12**, Node **24** (ou versão compatível com Vite 8, a partir de 22.12), PostgreSQL **16**.
- Internet para instalar dependências na primeira execução. Não há API paga exigida para o MVP.
- Windows: Python/Node/PostgreSQL instalados; use dois terminais no VS Code.
- Linux com MediaPipe: bibliotecas `libegl1`, `libgles2`, `libgl1` e `libglib2.0-0` (o nome pode variar por distribuição).

Não existe cópia de suas credenciais ou do seu banco neste ZIP. As fotos utilizadas nos testes foram sintéticas e as capturas de teste foram excluídas.

## Iniciar no Windows / VS Code

1. Extraia o ZIP e abra a pasta **vesteia** no VS Code.
2. No PostgreSQL/pgAdmin, crie um banco `vesteia`, se ainda não existir. **Faça backup antes de aplicar migrações em um banco existente.** Nenhuma migration apaga as tabelas antigas.
3. Primeiro terminal:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Se a ativação for bloqueada pelo PowerShell, use diretamente `.\.venv\Scripts\python.exe` no lugar de `python`; não precisa alterar a política do sistema.

4. Edite `backend/.env` com host, porta, banco, usuário e senha do **seu** PostgreSQL. Depois:

```powershell
python scripts/setup_db.py --seed
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

`setup_db.py` cria a estrutura que falta, liga registros legados à nova loja sem copiar/renumerar seus IDs e, com `--seed`, insere/atualiza exclusivamente a coleção `demo-*`. A execução repetida não duplica esses SKUs. Para aplicar somente a estrutura e expor seu catálogo anterior, omita `--seed`.

5. Segundo terminal:

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

6. Abra **http://127.0.0.1:5173**. A API documentada fica em **http://127.0.0.1:8000/docs**. Escolha uma peça, crie o perfil e compare os tamanhos.

## Iniciar no Linux/macOS

Na pasta backend: `python3 -m venv .venv`, `source .venv/bin/activate`, `pip install -r requirements.txt`, `cp .env.example .env`. Configure o banco e execute os mesmos comandos de setup/uvicorn. No frontend, use `npm ci` e `npm run dev`.

Também há `compose.yaml` para subir **somente PostgreSQL** em Docker, com volume persistente. Defina `POSTGRES_PASSWORD` no seu ambiente antes de `docker compose up -d`. Nesse caso, configure `DB_USER=vesteia`, `DB_NAME=vesteia`, a mesma senha e porta 5432. Não use `docker compose down -v` se quiser preservar o banco.

## Configuração

| Variável | Uso |
| --- | --- |
| DB_HOST / DB_PORT | Host e porta do PostgreSQL |
| DB_NAME / DB_USER / DB_PASSWORD | Banco e credenciais locais, somente backend |
| CORS_ORIGINS | Origens autorizadas, separadas por vírgula |
| VITE_API_BASE_URL | Endereço público da API, definido antes do build |

`.env` não deve ser versionado. Variáveis `VITE_*` são públicas; nunca coloque uma chave privada nelas. Não publique este backend de desenvolvimento diretamente na internet.

## Arquitetura

| Camada | Responsabilidade |
| --- | --- |
| frontend/src/App.jsx | Shell e navegação por hash, estado de páginas |
| features/catalog | Catálogo, filtros, cartões e apresentação das peças |
| features/profile | Onboarding, aparência, validação dos campos, perfil |
| features/fitting | Comparação, adaptador visual, fotografia, seleção de tamanho |
| features/commerce | Favoritos, sacola e look no navegador |
| services/mvpApi.js | Transporte HTTP, erros e tokens de captura em memória |
| backend/app/api/mvp.py | Contratos comerciais novos, perfis, comparação e sacola |
| repositories/catalog_repository.py | Catálogo normalizado PostgreSQL e ponte de SKU |
| repositories/legacy_bridge.py | Exposição não destrutiva dos produtos anteriores |
| services/comparacao_mvp.py | Comparação de medidas declaradas, explicação e confiança |
| adapters/catalog_adapter.py | Validação/normalização de entradas de e-commerce |
| services/photo_privacy.py | Acesso individual, expiração e exclusão da captura |
| api/provador.py + services existentes | Pipeline original de foto, qualidade, geometria e vestimenta |

Banco: `catalog_products → catalog_variants → catalog_sizes (medidas JSONB/estoque/legacy_product_id) → produtos`. `client_profiles` guarda o perfil anônimo. `sessoes_provador` guarda referências a arquivos privados fora do banco. O banco anterior é preservado e o catálogo novo mantém os IDs legados para o pipeline.

Favoritos, sacola e look são persistidos **neste navegador** e não são compartilhados entre dispositivos. O perfil tem ID aleatório e também é salvo no banco, mas não há autenticação/conta nem sincronização automática entre navegadores. **Excluir meus dados** remove o perfil do banco e as escolhas locais.

## Contratos da API

| Método / endpoint | Resultado |
| --- | --- |
| GET /health | Saúde do processo, não certifica conexão com o banco |
| GET /mvp/catalogo | Produtos normalizados com variantes e tamanhos |
| GET /mvp/produtos/{id} | Ficha normalizada |
| POST /mvp/produtos/{id}/comparar | variant_id, perfil, preferencia → tamanhos, razões, visual e recomendação |
| PUT /mvp/perfis/{uuid} | Salva perfil anônimo |
| DELETE /mvp/perfis/{uuid} | Exclui perfil |
| POST /mvp/carrinho/validar | Lista de size_id/quantidade → preço atual, disponibilidade e total |
| POST /provador/preparar | Multipart foto/produto_id → sessao_id e access_token |
| POST /provador/sessoes/{id}/executar | Pipeline original; exige Authorization: Bearer access_token |
| DELETE /provador/sessoes/{id} | Remove captura e arquivos; exige mesmo token |

CRUD `/produtos`, grade, `/avatar/vestibilidade`, endpoints anteriores e seus contratos foram mantidos. Os endpoints de captura passam a exigir token; a listagem global de fotos fica desativada para evitar expor arquivos de outras pessoas. Fotos anteriores sem token não ficam acessíveis pela API.

## Importar catálogo de outra loja

```powershell
cd backend
python scripts/import_catalog.py caminho-do-catalogo.json
```

O arquivo é um array de produtos com `external_product_id`, `nome`, `categoria` e `variantes`. Cada variante tem `sku`, `cor`, `preco`, `modelagem`, `imagem_url`, `metadata` e `tamanhos`. Cada tamanho tem `label`, `sort_order`, `estoque` e `medidas`. Um exemplo completo está em `docs/catalogo-exemplo.json`.

A ordem é a da loja; não há conversão automática de PP para XS ou de números entre marcas. SKU não pode pertencer a dois produtos. Importar atualiza os registros enviados e preserva IDs; não apaga automaticamente os produtos/tamanhos omitidos. Para retirar um SKU da venda, informe estoque zero. Os registros anteriores sem ordem explícita conservam a ordem de cadastro.

Semântica das medidas: `largura_cm` é a largura da peça aberta; `torax_cm`, `cintura_cm` e `quadril_cm` são circunferências da **peça**; `ombros_cm` é a distância entre os ombros; `pe_cm` é o comprimento útil interno informado pela loja; `comprimento_cm` é o comprimento da peça. Valores inconsistentes de um fornecedor não são certificados automaticamente.

## Precisão e limites

- Foto monocular sem escala válida fornece pose/proporções e qualidade. Não gera centímetros, peso ou circunferências reais. O fluxo comercial não usa a foto como prova métrica.
- A comparação por medidas usa heurísticas explícitas de folga/modelagem/preferência, não uma validação clínica/antropométrica. Confiança **moderada** significa eixos cadastrados comparados; não é porcentagem de acerto. Um único eixo oferece confiança limitada. Altura/peso usam a sugestão anterior com confiança baixa.
- Se todos os tamanhos medidos são menores que o corpo informado ou sem estoque, não se recomenda um tamanho incompatível.
- Aparência, pele e cabelo não entram no cálculo da recomendação. A geometria visual continua aproximada.
- A camada Natural usa bases artísticas recortadas para camiseta preta. Outras cores, categorias, looks e personalizações usam o renderer ilustrado. Esses resultados são 2D e não reproduzem física de tecido ou um corpo individual fotorrealista.
- `generated_tryon.py` oferece uma fronteira de adaptador; geração fotorrealista individual por serviço externo está **não configurada**, com fallback honesto para 2D.
- Sacola não reserva estoque; não há pagamento, frete, checkout, autenticação comercial ou conector live de plataforma externa. O importador neutro está funcional.

## Privacidade das fotos

JPEG/PNG/WebP até 10 MB e 25 megapixels, com verificação do conteúdo, nomes internos aleatórios e token específico por sessão. Os arquivos não são servidos publicamente. A foto pode ser excluída na tela e a aplicação tenta excluí-la ao sair desse fluxo.

A captura expira em 24h e não pode mais ser acessada. Com a API ligada, a limpeza ocorre a cada 10 minutos; também ocorre ao criar captura. Se a API estiver desligada, a remoção física acontece na próxima execução ou por `python scripts/purge_photos.py`. Agende esse comando no ambiente de produção para uma política operacional de retenção. Nenhuma foto é enviada a treinamento ou serviço externo pelo código entregue.

## Verificação

Backend: use **um banco isolado cujo nome termine em `_test`**, configure o ambiente/.env para ele, instale `requirements-dev.txt` e execute `python -m pytest tests -q`. Os testes aplicam migrations/seed nesse banco, criam e removem capturas sintéticas. Não execute em produção.

Frontend: `npm run build`, `npm run lint`. Para testes de interface, mantenha API/DB e Vite ligados, execute `npx playwright install chromium` e `npm run test:e2e`. `TEST_BASE_URL` troca a origem de teste. Os testes usam um contexto de navegador isolado e geram capturas em `docs/screenshots/`.

Resultados executados e limitações de validação estão em `docs/VALIDACAO.md`. A tela legada mantém dois avisos de dependências de efeitos no lint; os módulos novos não têm erros. A compilação funciona.

## Problemas comuns

- “Vamos conectar sua loja”: confira o servidor FastAPI, `.env`, PostgreSQL, migrations e URL da API. A UI não inventa um catálogo quando o banco está indisponível.
- `unaccent` ausente: execute `setup_db.py`; a migration instala essa extensão. O usuário do banco precisa poder instalá-la.
- Erro de conexão: confira DB_PORT, credenciais e se o banco foi criado.
- Erro CORS: adicione a origem correta em CORS_ORIGINS e reinicie a API.
- Erro MediaPipe no Linux: confira bibliotecas EGL/GLES e Python 3.12. O modelo `pose_landmarker_lite.task` já está incluído.
- Foto sem corpo visível: envie nova captura frontal completa, sem oclusão, com boa luz. Não trate ausência de landmarks como análise bem-sucedida.
- Captura expirada: envie outra; o token não é persistido no navegador após recarregar.
- Sem recomendação: informe os eixos pertinentes à categoria e confira tabela/estoque da peça. Calçado exige comprimento do pé, não peso/altura.

## Próximas etapas

Validação de tabelas e regras de folga com lojas/pessoas; catálogo real de fornecedor; autenticação e sincronização; controles de acesso para CRUD administrativo antes de publicação; conector B2B específico; infraestrutura para geração visual; malha 3D/calibração/tecido quando houver base adequada; checkout integrado externo. Consulte `docs/MANUTENCAO.md`.
