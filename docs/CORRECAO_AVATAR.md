# Manequins e camadas de vestuário

Ilustrado usa os PNGs de manequim criados e aprovados; não usa recortes de corpo já vestido. Natural mantém o avatar simples com aparência do perfil. Os dois estilos usam GarmentLayer e garmentModel para a mesma roupa. Não há migração de banco nesta atualização.

## Regras de composição

Peça única é inicial e mostra só o SKU em teste. Look completo compõe itens ativos e o SKU atual. Vestido ocupa torso e parte inferior; elimina camiseta/calça/saia/bermuda anteriores. A peça atual tem prioridade. Base neutra mostra apenas o corpo com cobertura íntima, sem apagar o look.

## Dimensões

A largura plana e comprimento do SKU controlam escalas independentes. Na falta de largura plana, usam-se tórax, quadril ou cintura explicitamente cadastrados. O corpo é fixo entre os cartões; não deduzimos medidas corporais da foto. Dimensões ausentes aparecem como não cadastradas, sem diferenças fictícias. São proporções gráficas relativas a bases artísticas, não escala física do manequim ou simulação de tecido.

Enquadramento Corpo inteiro/Detalhe da peça é o mesmo para toda a grade. Os cartões mostram diferenças em cm em relação ao primeiro tamanho. O zoom não se adapta ao tamanho individual, pois isso esconderia diferenças.

## Aparência de cada variante

1. metadata.visual.roupa_png_url: PNG frontal recortado e transparente, cobre a geometria da categoria; tamanho e proporção artística devem corresponder à área da peça.
2. metadata.visual.textura_url e textura_crop: foto/tecido projetados dentro da silhueta. Crop x/y/w/h são frações de 0 a 1 da imagem. A imagem_url da variante também é usada como textura automaticamente; crop central genérico pode precisar ajuste.
3. metadata.visual.estampa_url ou estampa_texto: arte transparente ou texto literal sobre a cor da variante. estampa_cor controla cor do texto. estampa_posicao {x,y,w,h} posiciona arte em coordenadas normalizadas da peça.

Uma foto comercial NÃO é segmentada automaticamente nem deformada como tecido físico. O crop central é aproximado e pode perder ou deslocar estampas fora do centro; use crop específico ou PNG frontal/arte separada para fidelidade. Não copiados logotipos de uma variante para outra sem fonte. Sem imagem ou estampa, a peça usa sua cor cadastrada e o cartão informa a ausência de arte. Falha de imagem mantém a silhueta/color e outras artes disponíveis.

A camiseta preta VesteIA fornecida possui imagem com logo e um crop conhecido, aplicado sem redesenhar o texto. O teste de VSI/violeta usa catálogo simulado; não altera automaticamente o catálogo do usuário. Consulte catalogo-visual-exemplo.json para cadastrar uma variante com essa estampa via o importador existente.

## Responsabilidades

frontend/src/features/fitting/garmentModel.js: composição, medidas, aparência e enquadramento compartilhado.
GarmentLayer.jsx: categoria/silhueta, fontes visuais, cor, estampa, costuras e degradação por falha de asset.
AvatarView.jsx: base PNG de manequim + camadas.
AvatarIllustration.jsx: base SVG personalizada + mesmas camadas.
FittingRoom.jsx: SKU selecionado, modo peça/look/base, enquadramento e comparação tabular.

## Validação da atualização

Build passou. Lint sem erros; dois avisos de dependências de efeitos permanecem no provador legado. Testes em navegador Chromium com API simulada: seis categorias isoladas, crescimento da largura visual entre SKUs, base constante, foto com logo, estampa VSI e cor por variante, falha de imagem, look/base, feminino, ambos os estilos, enquadramento igual e mobile sem overflow. A suíte original continua exigindo backend/PostgreSQL; não foi rerodada nesta atualização só de frontend.

Executar a regressão visual independente: na pasta frontend, node tests/garment-visuals.mjs (requer Chromium do Playwright instalado). Ela abre e fecha servidor próprio na porta 5193; não escreve no banco. Screenshots com nomes Teste são fixtures do teste, não o catálogo final.

## Aplicar no Windows

Pare npm run dev com Ctrl+C. Substitua frontend/src e copie frontend/public/assets do ZIP sobre os arquivos atuais. Reinicie npm run dev e recarregue a página. Não substitua backend/.env, banco ou node_modules. Não precisa rodar seed ou migration para esta correção.
