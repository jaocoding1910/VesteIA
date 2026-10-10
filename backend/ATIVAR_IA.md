# Prévia realista com IA — atualizar seu VesteIA atual

A integração chama Google Cloud Virtual Try-On (`virtual-try-on-001`) com uma imagem do avatar/pessoa e uma foto da peça. O resultado aparece em **Prévia realista com IA** dentro do provador. Esta função não altera o banco ou a comparação de tamanhos. P/M/G/GG continuam usando as medidas; a imagem generativa mostra aparência geral e não muda automaticamente com o tamanho.

## Projeto já integrado

Todos os arquivos da IA já estão nas pastas corretas deste ZIP. Não é necessário copiar módulos individualmente. Primeiro abra o aplicativo seguindo LEIA_PRIMEIRO.md. Os atalhos já instalam requirements-ai.txt.

Sem conta configurada, a aplicação mostra **IA não configurada**. Não existe geração falsa ou fallback apresentado como IA.

## Configuração Google Cloud, uma vez

É necessário um projeto Google Cloud com faturamento habilitado, API de IA do Google Cloud (`aiplatform.googleapis.com`) habilitada e permissão para invocar o modelo. O serviço cobra por uso; confira preço e disponibilidade na documentação oficial antes de habilitar. Não é uma API incluída na assinatura ChatGPT.

1. Crie ou selecione seu projeto em https://console.cloud.google.com/.
2. Habilite o faturamento e a API de IA acima. O nome exibido pode ser Vertex AI/Agent Platform conforme o console. Sua conta precisa das permissões apropriadas (por exemplo, Vertex AI User).
3. Instale a Google Cloud CLI seguindo https://cloud.google.com/sdk/docs/install.
4. No terminal, substitua `SEU_PROJECT_ID` pelo ID do projeto (não pelo nome de exibição):

```powershell
gcloud auth application-default login
gcloud auth application-default set-quota-project SEU_PROJECT_ID
```

O login abre no seu navegador. Mantenha essas credenciais somente no computador; não precisa enviá-las aqui.

5. Dentro de `backend`, instale apenas a dependência adicional:

```powershell
.\.venv312\Scripts\python.exe -m pip install -r requirements-ai.txt
```

6. Acrescente ao FINAL do `.env` existente, mantendo DB_HOST, DB_NAME, DB_USER, DB_PASSWORD e os demais valores:

```dotenv
TRYON_ENABLED=true
TRYON_GOOGLE_PROJECT=SEU_PROJECT_ID
TRYON_GOOGLE_REGION=us-central1
TRYON_GOOGLE_MODEL=virtual-try-on-001
```

Não coloque a senha do PostgreSQL nesses campos. A autenticação é feita pelas credenciais locais da Google Cloud CLI. `TRYON_GOOGLE_ACCESS_TOKEN` é uma alternativa opcional de token temporário para testes; não é necessária com o login acima e expira.

7. Pare apenas o backend com Ctrl+C e inicie novamente, dentro de `backend`:

```powershell
.\.venv312\Scripts\python.exe -m uvicorn app.main:app --reload
```

O frontend pode continuar rodando. Atualize a página do navegador para recarregar o status.

## Testar

Abra uma peça → **Prévia realista com IA**. Escolha **Meu avatar** ou **Minha foto**. Uma foto real de corpo inteiro, com roupa e boa iluminação, é uma referência mais adequada para testar fidelidade à pessoa; o avatar é uma referência sintética.

Opcionalmente envie uma foto PNG/JPG/WebP da roupa. Sem upload, a função usa `variant.metadata.visual.tryon_image_url` ou `variant.imagem_url` do catálogo, rasterizando SVG no navegador. Desenhos simples de camiseta/calça no catálogo não equivalem a fotos reais: envie uma foto da peça para testar melhor.

Marque a autorização de envio ao Google Cloud e clique **Gerar prévia realista**. A geração só ocorre nesse clique. Aguarde. Trocar P/M/G não dispara outra geração. **Apagar prévia** remove o resultado desta página.

A IA pode alterar rosto, corpo, textos, estampas e cortes, ou recusar entradas. Avalie as quatro peças com imagens reais antes de considerar a qualidade aprovada. Categorias inicialmente habilitadas: partes superiores, calças, shorts/bermudas, saias e vestidos; isso não garante desempenho igual entre elas. Bonés e calçados permanecem no renderer existente.

## Falhas comuns

- **IA não configurada**: revise os quatro campos do `.env` e reinicie o backend.
- **Autenticação não configurada**: instale requirements-ai.txt e execute o login ADC acima.
- **Erro 403 do provedor**: confira projeto, faturamento, API habilitada e permissão de invocação.
- **Modelo/região indisponível**: confira disponibilidade atual e ajuste os campos respectivos.
- **Sem imagem ou entrada recusada**: tente uma foto real vestida e uma foto completa da roupa.
- **Limite atingido**: aguarde. Não existe repetição automática da chamada paga.

## Validação e limites

Testados: contrato REST, normalização de fotos e remoção de metadados, configuração desabilitada sem chamada, consentimento, variante inválida e concorrência. Interface testada com exportação do avatar, upload, exibição/apagamento do resultado e tamanhos sem novas chamadas. Build, ESLint e regressões de loja e personalização passaram. **O provedor foi simulado nos testes. Não houve geração real nem avaliação de qualidade com Google Cloud porque nenhuma credencial foi configurada neste ambiente.** A captura entregue mostra apenas a interface sem configuração, não um resultado de IA.

Nenhuma foto ou resultado é gravado no PostgreSQL ou em arquivos permanentes do VesteIA. Uploads podem usar buffers/arquivos temporários do framework, fechados após a requisição. Processamento externo segue os termos do Google Cloud. Fechar a página durante uma chamada não garante cancelamento do processamento/cobrança externos.

Esta entrega destina-se ao teste local, com backend em 127.0.0.1. Antes de expor a geração paga numa loja pública, implementar autenticação, isolamento por loja, limites por usuário, orçamento e monitoramento. O bloqueio de concorrência desta entrega vale por processo e não substitui esses controles.

Documentação de referência:
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/generate-virtual-try-on-images
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/vto/virtual-try-on-001
- https://cloud.google.com/docs/authentication/set-up-adc-local-dev-environment
