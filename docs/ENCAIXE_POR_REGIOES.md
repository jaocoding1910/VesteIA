# VesteIA 1.4 — encaixe por regiões

## Instalação
Extraia o projeto inteiro em pasta nova. Reutilize seu backend/.env e siga o README. Execute `python scripts/setup_db.py --seed` para atualizar os assets demonstrativos. Inicie backend e frontend nos dois terminais. Abra um produto e selecione Humano no editor, Peça isolada e Detalhe da peça para comparar.

## Esta integração
As camadas passam por uma malha afim de 60 triângulos por peça. Imagem da roupa, cor e estampa são compostas antes da deformação e compartilham o mesmo mapeamento. Gola e contato dos ombros têm controle próprio, separando o encaixe superior da largura do tronco. Manga, cintura, quadril e barra alteram regiões da malha. Uma sombra de contato integra as bordas ao corpo. O avatar permanece fixo entre as grades.

Largura/comprimento vêm de `tamanho.medidas`. Os nomes P/M/G/GG não determinam a geometria. Os valores do catálogo permanecem intactos. As razões visuais são calibradas em relação ao asset, não representam uma reconstrução física em centímetros do avatar. Quando faltam medidas, os valores de referência são aproximações.

## Dados de uma nova variante
`metadata.visual.roupa_png_url`: imagem frontal recortada somente da roupa, transparente e registrada no molde da categoria. Alternativamente `roupa_genero_urls`: assets masculino/feminino. Um recorte próprio deve preservar os detalhes do produto real; uma foto arbitrária da vitrine não é automaticamente segmentada ou encaixada por esta integração.

`metadata.visual.medidas_referencia`: dimensões do tamanho usado para preparar o asset. Exemplo: `{"largura_cm":52,"comprimento_cm":70,"manga_cm":22,"ombros_cm":46}`. Cada tamanho fornece suas medidas reais em `medidas`. As medidas de referência configuradas por variante prevalecem sobre as do produto.

`metadata.visual.encaixe_humano`: registro por gênero do asset no corpo-base. Exemplo de calça: `{"feminino":{"subir_cintura_px":65},"masculino":{"subir_cintura_px":20}}`. É uma calibração gráfica em pixels do molde, não uma medida física. Ajusta a cintura mantendo o final da perna. Os recortes demonstrativos foram corrigidos para excluir o tênis do asset da calça.

`metadata.visual.estampa_url`/`estampa_texto`: camada adicional opcional, somente para estampas que não estejam incorporadas à imagem; não duplicar logotipos existentes. As imagens são mantidas, não recriadas por IA. Pode ocorrer reamostragem/pequena perda de nitidez na deformação.

Camiseta/calça demonstrativas continuam com o tecido dos anexos e o logo demonstrativo VesteIA; não são fotos de produtos de uma loja conectada. A projeção de cor de demonstração é aproximada. Para fidelidade de uma loja, fornecer asset próprio de cada variante já na cor real.

## Categorias e limites
A superfície é compartilhada pelos renderizadores atuais: camiseta e suas famílias aproximadas, calça/bermuda, saia, vestido e calçado. Cada categoria tem geometria própria; novos produtos precisam de asset calibrado adequado. As medidas locais desta iteração são detalhadas em camiseta e calça, e cintura/quadril/barra em saia/vestido. Calçado ainda usa a geometria anterior e a superfície compartilhada; não houve validação anatômica nova de tênis. Boné/acessórios de cabeça ainda precisam de um renderer próprio e não estão implementados nesta versão.

Não há simulação física, malha 3D, aprendizado de virtual try-on ou reconstrução de identidade. Não há promessa de encaixe perfeito nem leitura automática de qualquer imagem do catálogo. O modo geométrico anterior continua como aproximação quando falta asset preparado; não deve ser apresentado como reprodução fiel do produto. Esta versão melhora o encaixe 2D e deixa a fronteira de integração explícita.

## Verificações
`npm run test:mesh`: vértices da transformação afim, medidas regionais independentes e imutabilidade dos dados. `npm run test:model`: medidas e calibração por variante. Fluxo real: PostgreSQL/API, avatar/foto/edição, grades, estampas, peça isolada/look/base, sacola, persistência e mobile. `npm run test:visual`: renderizadores das seis categorias com API simulada. Build e lint (dois avisos no componente legado).
