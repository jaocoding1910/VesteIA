# Verificação da entrega — 30/09/2026

## Ambiente executado
Python 3.12, Node 24.19, PostgreSQL 16 e navegador Chromium headless. Banco temporário isolado `vesteia_test`. Nenhum banco do usuário foi acessado. Fotos de teste: imagem sintética de modelo e imagem branca sem pessoa.

## Backend — 19 casos
- Inicialização/migrações aditivas e seed repetido sem duplicar SKUs.
- Catálogo dinâmico e preservação da ordem numérica.
- Comparação por medidas reais declaradas e razões diferentes por variante.
- Aparência masculina/feminina, pele e cabelo sem alterar a recomendação.
- Ausência de medidas sem inventar ajuste; confiança limitada/baixa explicitada.
- Estoque zerado e tamanhos insuficientes sem recomendar opção inadequada.
- Importador com ordem externa preservada e rejeição de tamanhos duplicados.
- Perfil, validação de campos, exclusão, variante inválida e comparação HTTP.
- Sacola com preço atual, estoque, IDs inexistentes e agregação de SKU duplicado.
- Upload inválido, MIME rejeitado, captura válida sem pessoa e resposta de qualidade.
- Acesso privado com token; exclusão e bloqueio de listagem global.
- Contratos CRUD/grade/vestibilidade anteriores funcionando.
- Detecção positiva, renderer pronto e vestimenta posicionada nas seis categorias.
- Expiração com exclusão física dos arquivos.

`python -m pytest tests -q`: **19 passed**. A versão de Starlette emite um aviso de depreciação referente a httpx no TestClient; ele não afetou os contratos testados.

## Interface
`npm run build`: compilação de produção concluída. `npm run lint`: zero erros; dois avisos de dependências em efeitos da tela legada, documentados e mantidos fora da nova experiência.

`npm run test:e2e`: catálogo, busca vazia, onboarding, perfil/medidas, recomendação, mudança de tamanho, favoritos, sacola com estoque, persistência após reload, look, apresentação feminina, envio/análise de foto com renderer e retorno ao avatar, desktop, mobile 390px/320px sem overflow horizontal, grade numérica e rota recarregada. Sem erros JavaScript de página.

## Revisão visual
Capturas reais em `docs/screenshots/`: loja desktop, provador desktop e provador mobile. A revisão identificou e corrigiu escala do logotipo e encaixe das bases naturais. A composição segue a referência; as bases artísticas e detalhes de conteúdo não são uma reprodução pixel a pixel da fotografia de referência.

## Limites da validação
Não há comprovação de precisão de ajuste com participantes reais, tecidos ou tabelas de marcas. O teste positivo de foto usa um modelo sintético; não representa diversidade completa de poses/corpos/câmeras. Não foram testados Safari, hardware de câmera real, pagamento ou conector comercial live. O compose opcional não foi executado: PostgreSQL foi testado diretamente. Publicação na internet não foi realizada.

O MVP está preparado para uso e revisão local no VS Code. Os controles administrativos/auth/rate limiting ainda precisam ser aplicados antes de expor o backend publicamente, conforme README.


Atualização de camadas: ver CORRECAO_AVATAR.md. Nova suíte frontend/tests/garment-visuals.mjs roda isolada com catálogo simulado: seis categorias × dois gêneros × dois estilos; tamanhos, corpo fixo, estampas/falha de arquivo, enquadramento, look e mobile. Screenshots camiseta-estampa-tamanhos.png, camiseta-detalhe.png, bermuda-peca-unica.png, peca-unica-mobile.png correspondem a fixtures. Testes backend anteriores não foram repetidos nesta alteração do frontend.
