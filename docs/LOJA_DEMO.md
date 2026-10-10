# VesteIA 1.5.5 — loja FORMA demonstrativa

A loja fictícia reúne camiseta, calça, bermuda e vestido. Na aba **Loja demo**, abra uma peça e clique **Experimentar com VesteIA**. O provador abre dentro da loja; selecione um tamanho e clique **Usar este tamanho na loja**. O tamanho retorna à página do produto. A compra é demonstrativa, sem pedidos ou pagamentos.

## 1. Preparar banco separado

No terminal do VS Code, partindo da pasta `vesteia`:

```powershell
cd backend
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
```

Crie `backend/.env` a partir de `.env.example`, mantendo seu usuário, senha, servidor e porta do PostgreSQL. Com o PostgreSQL iniciado:

```powershell
.\.venv312\Scripts\python.exe scripts/setup_loja_demo.py --database vesteia_loja_demo
```

O script cria um banco separado e importa quatro produtos com P/M/G/GG. Não apaga o banco anterior nem substitui seu `.env`. O usuário PostgreSQL precisa ter permissão para criar bancos; se não tiver, peça ao administrador para criar `vesteia_loja_demo` e execute novamente. Se o banco já contiver outro catálogo, o script recusa a importação.

Somente depois de aparecer a mensagem de conclusão:

```powershell
Copy-Item .env .env.original
Copy-Item .env.loja-demo .env
.\.venv312\Scripts\python.exe -m uvicorn app.main:app --reload
```

Se `.env.original` já existir, use outro nome para preservar a cópia anterior. Para voltar ao banco anterior, restaure essa cópia como `.env` e reinicie o backend. Não compartilhe esses arquivos: contêm sua senha.

## 2. Frontend em outro terminal

Partindo da pasta `vesteia`:

```powershell
cd frontend
npm install
npm run dev
```

Abra o endereço mostrado pelo Vite e clique **Loja demo** (ou acrescente `/#loja`). Para testar sem misturar sacola/look salvos no navegador com o catálogo anterior, use uma janela privativa. O frontend não precisa de ambiente virtual Python.

## O que esta versão demonstra

- Página de produto, preço, tamanhos e medidas do catálogo.
- Provador 2D integrado com personalização existente e comparação de tamanhos.
- Retorno validado por origem, janela, canal, produto, variante e tamanho.
- Vestido e bermuda com novos recortes PNG; camiseta e calça aproveitam os recursos existentes.
- Importação repetível por IDs externos/SKUs; banco separado sem operações de exclusão.

A projeção visual continua sendo uma aproximação 2D, não uma simulação física do tecido. Medidas, preços e estoque da FORMA são fictícios. Esta integração usa a mesma origem para loja e provador. Uma loja externa precisará de integração autorizada, configuração de origens, identificação da loja e autenticação apropriadas; este pacote não modifica sites de terceiros.

## Validação

Build e ESLint; testes de modelos e comportamento existentes; teste de navegação com catálogo/API simulados. O teste de navegador cobre as quatro peças, abertura do iframe e retorno do tamanho G. A criação real do PostgreSQL deve ser validada na instalação local; o ambiente de entrega não tem servidor PostgreSQL disponível.
