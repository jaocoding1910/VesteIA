# VesteIA 1.3 — corpo realista e peças separadas

## Instalar
Extraia em pasta nova, configure backend/.env e siga o README para instalar dependências. Execute `python scripts/setup_db.py --seed` para carregar texturas das camisetas/calças demonstrativas. Inicie backend e frontend. No editor selecione **Humano · corpo realista**.

## Visual
O acabamento humano agora usa uma base humana fotográfica completa gerada, substituindo a composição de rosto sobre corpo estilizado. A masculina tem shorts neutros; a feminina usa top esportivo e shorts neutros. Essas coberturas fazem parte da base, não são itens do look.

Peça isolada: somente a peça selecionada veste essa base. Calça deixa o tronco visível (e top neutro feminino); camiseta deixa a cobertura neutra inferior. Look completo continua juntando itens de regiões distintas. A base é a mesma entre os tamanhos comparados.

Camiseta e calça mantêm texturas separadas por gênero dos exemplos enviados, cor da variante e estampa independente. Os outros renderizadores mantêm seu comportamento anterior.

## Limites
Visualização frontal 2D, sem reconstrução de identidade nem simulação física do tecido. As bases têm anatomia própria e podem ter pequenas diferenças dos exemplos; proporções podem ser editadas. Tamanho/caimento alteram a camada gráfica, não geram novas dobras ou garantem ajuste real. Cor/cabelo/pele personalizados estão no modo manequim; no humano permanecem os da base. As medidas usadas na recomendação são fornecidas pelo usuário, não deduzidas em centímetros de uma foto.

## Assets gerados
Ferramenta embutida de geração de imagens. Prompts: base masculina adulta fotográfica, frontal, pose neutra, shorts esportivos opacos, pés descalços, fundo transparente, alinhamento corporal 1024×1536; base feminina adulta fotográfica, frontal, top esportivo de cobertura alta e shorts esportivos opacos, mesma pose e alinhamento. Uma primeira tentativa feminina foi bloqueada e não produziu asset; a base utilizada adota cobertura esportiva maior.

Arquivos: frontend/public/assets/avatar-humano-masculino-v2.png e avatar-humano-feminino-v2.png. Os originais anteriores foram preservados.
