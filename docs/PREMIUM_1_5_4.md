# VesteIA 1.5.4 — interface e provador 2D

## Base e análise antes das alterações
Foi usado o ZIP 1.5.3 enviado nesta conversa, extraído em uma pasta separada. Não houve reconstrução do projeto nem mudança de banco. O prompt anexado foi lido como especificação; o vídeo de 58,35 segundos foi inspecionado em quadros sequenciais, com atenção ao trecho do site no final.

Arquitetura preservada:

| Responsabilidade | Arquivos principais |
|---|---|
| Rotas hash, header, perfil e telas | frontend/src/App.jsx |
| Catálogo, busca e favoritos | features/catalog/Catalog.jsx, useCatalog.js, catalogModel.js |
| Estado e persistência | features/commerce/Store.jsx; localStorage vesteia:mvp:2 |
| Comparação e seleção | features/fitting/FittingRoom.jsx, SizeCard.jsx, useComparison.js |
| Avatar e aparência | AvatarView.jsx, HumanAvatarBody.jsx, SmoothAvatarBody.jsx, avatarModel.js |
| Peças e camadas | garmentModel.js, lookRules.js, renderers/garments/registry.js |
| Molde, medidas, estampa e deformação | GarmentLayer.jsx, ClothSurface.jsx, clothMesh.js, geometry.js |
| Editor, fotografia e salvamento | features/profile/ProfileEditor.jsx, PhotoAvatarSource.jsx |
| Contrato e comparação na API | backend/app/api/mvp.py, services/comparacao_mvp.py |
| PostgreSQL e catálogo externo | backend/app/database, repositories e adapters, preservados |
| Provador anterior e pipeline de foto | LegacyProvador.jsx e serviços existentes, preservados |

## Mudanças entregues
- Home com provador funcional em destaque, alternância masculino/feminino, entrada direta no provador, CTA para coleção, sequência de três passos e cards de produtos.
- Identidade própria em tons escuros, lavanda e superfícies neutras; tokens de movimento e acabamento em Premium.css. Não usa imagens ou marca do site do vídeo.
- Header fixo no desktop, busca com atalho /, estados ativos, foco visível e link de pular conteúdo sem trocar a rota hash.
- Cards sobem 6 px no hover com sombra progressiva. Botões sobem 2 px, e toque/clique tem feedback de pressão. Esses valores vêm da especificação, não de uma medição precisa do vídeo.
- Blocos fora da tela entram com IntersectionObserver, fade e deslocamento de 14 px. Efeitos de hover só rodam em dispositivos que suportam hover real. prefers-reduced-motion elimina animações e mantém o conteúdo disponível.
- Editor separado em AvatarControls: quatro estilos da base existente (raspado, curto liso, crespo e longo liso), mini cartões, oito opções de superfície/pele (incluindo tom original), seis cores naturais de cabelo e cor personalizada.
- Presets Slim/Padrão/Robusto conservam os valores persistidos estreito/medio/largo. Mudança de largura é suave e limitada ao corpo, sem alargar o rosto. Proporções de tronco e pernas continuam ajustáveis.
- Altura em cm não escala mais automaticamente a imagem: segue disponível, opcional, para recomendação. Os presets não inventam medidas físicas.
- Caimentos Justo, Slim, Padrão, Solto, Amplo e Oversized, compatíveis com a API atualizada. As medidas cadastradas permanecem intactas; manga, ombro, cintura, quadril e barra mantêm o modelo local existente.
- Base esportiva é substituída quando há peça em teste. Cobertura íntima aparece apenas onde não há uma peça cobrindo a região. Editor também mostra a superfície lisa de trabalho. Base neutra permite voltar à base anterior.
- A pintura opaca do tecido recebeu uma borda discreta de contato para reduzir frestas, sem recolorir estampas de imagens arbitrárias. Logos, imagens e cores do catálogo continuam passando pela malha existente.
- Casaco/jaqueta passaram a ter uma região externa independente da camiseta; suas formas continuam aproximadas, como já indicado no registry.

## Bugs corrigidos
1. O seletor de tronco oferecia opções de cabelo (crespo e textos “liso”), inválidas no contrato da API. Agora contém somente Curto/Médio/Longo, e valores antigos inválidos são normalizados ao salvar.
2. A peça atual podia continuar aparecendo depois de removida do look, pois era reinserida como produto em teste. A remoção/ocultação agora é respeitada no modo Look completo.
3. selectedGarments descartava a peça atual salva mesmo quando showProduct era false. O look agora preserva o item salvo quando não há produto em teste substituindo-o.
4. Roupa base íntima ficava desenhada mesmo sob uma região selecionada. A cobertura é controlada por regiões.
5. A home excedia a largura de 320 px: grid e tipografia foram ajustados e testados.
6. A falha ao carregar uma imagem ficava presa entre variantes. Agora o fallback é por URL, e famílias aproximadas têm uma ilustração de catálogo em vez de ficar vazias.
7. Conflitos de CSS de posição/contraste foram corrigidos na etiqueta da peça e nos favoritos.
8. O link de pular conteúdo alterava a navegação hash. Agora foca o main sem trocar de página.

## Performance
- Um único conjunto de camadas SVG por avatar é definido e reutilizado com use nas regiões de cabeça/tronco/pernas; antes, a composição React e a malha eram duplicadas. Teste confirma uma instância de HumanAvatarBody por cartão.
- Atlas de cabelos são carregados por promessa compartilhada, com remoção do cache se falharem; o cache limitado de composições por cor continua ativo.
- A malha de tecido é memoizada por categoria, medidas e caixa de geometria.
- Um observador de interseção por tela, com limpeza ao sair; sem listener permanente de scroll ou movimento de mouse.
- Nenhuma nova dependência de animação ou renderização. Bundle principal: cerca de 264,9 kB / 84,6 kB gzip. Não foi feito benchmark de FPS, portanto não há promessa numérica de desempenho.

## Relação com o vídeo
O vídeo mostra principalmente um hero com tipografia marcante, CTA destacado e navegação por seções com respiro e alternância de superfícies. Esses princípios orientaram hierarquia, ritmo da home e profundidade visual. Não foi possível medir com precisão efeitos individuais de mouse na filmagem; hover, fade/reveal e feedback de toque seguem o prompt, adaptados ao VesteIA.

## Testes executados
- npm run build: passou.
- npm run lint: zero erros, dois avisos preexistentes de dependências de hooks em LegacyProvador.
- test:model, test:mesh, test:look, test:base, test:personalization, test:visual: passaram.
- test:premium: masculino/feminino, camiseta/calça isoladas, look completo, troca sem remover a outra região, remoção da peça atual e de outra região, persistência de pele/cabelo/cor/corpo, dois novos caimentos, hover, atalho /, tabs por teclado, Escape, sacola, 320/390/768/1024/1440 px e reduced-motion. Passou com API simulada.
- Backend: 17 testes passaram (test_finalizacao.py e test_premium.py), incluindo contrato dos seis caimentos e preservação de medidas. Python 3.12.
- Prévias são screenshots da aplicação com produtos demonstrativos simulados, não montagens de design.
- Não foi executado o teste de integração que escreve em PostgreSQL nem a análise real MediaPipe de fotos. Esses fluxos existentes não foram alterados; não havia um banco isolado _test configurado no ambiente desta entrega. A validação da API nova cobre os contratos e a comparação, não uma transação real no seu banco.

## Limites e próximos passos
A renderização continua frontal e 2D. O corpo liso é sintético; o rosto é o da base. Não há escolha de rostos novos nem estilos extras de cabelo além dos quatro disponíveis. Novos cabelos podem ser acrescentados por atlas próprios. Caimento é aproximação visual, não física de tecido ou garantia de tamanho. Para cada produto ficar fiel a todos os detalhes, o catálogo precisa de imagens/recortes preparados, medidas e registro de encaixe. Casacos e outras famílias aproximadas precisam de moldes específicos para evoluir a fidelidade. O futuro 3D continua separado; não foi ativado nesta entrega.

## Arquivos alterados/criados
- README.md
- backend/app/api/mvp.py
- backend/app/services/comparacao_mvp.py
- backend/requirements-test.txt
- backend/tests/test_premium.py
- docs/ABRIR_1_5_4.md
- docs/ESPECIFICACAO_USUARIO.txt
- docs/PREMIUM_1_5_4.md
- docs/REFERENCIAS_1_5_4.json
- docs/auditoria-fontes.json
- frontend/package-lock.json
- frontend/package.json
- frontend/src/App.jsx
- frontend/src/Premium.css
- frontend/src/components/ui/useMotion.js
- frontend/src/features/catalog/Catalog.jsx
- frontend/src/features/catalog/CatalogHero.jsx
- frontend/src/features/catalog/ProductImage.jsx
- frontend/src/features/fitting/AvatarView.jsx
- frontend/src/features/fitting/AvatarVisualTabs.jsx
- frontend/src/features/fitting/ClothSurface.jsx
- frontend/src/features/fitting/FittingRoom.jsx
- frontend/src/features/fitting/GarmentLayer.jsx
- frontend/src/features/fitting/HumanAvatarBody.jsx
- frontend/src/features/fitting/LookPanel.jsx
- frontend/src/features/fitting/avatarModel.js
- frontend/src/features/fitting/garmentModel.js
- frontend/src/features/profile/AvatarControls.jsx
- frontend/src/features/profile/ProfileEditor.jsx
- frontend/src/renderers/garments/registry.js
- frontend/tests/look-rules.mjs
- frontend/tests/premium-experience.mjs

Além destes: documentação, versão de package/package-lock, auditoria e capturas da entrega.
