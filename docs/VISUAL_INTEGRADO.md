# VesteIA 1.2 — visual integrado

Esta atualização utiliza os PNGs enviados como referência para os rostos masculino/feminino e para a textura da camiseta e da calça. As peças são recortadas separadamente, sem incluir a outra vestimenta. O corpo-base existente foi preservado e recebe tonalidade humana.

## Como atualizar

Extraia o projeto completo em uma pasta nova. Configure o backend com o seu .env (não incluído) conforme o README. Execute `python scripts/setup_db.py --seed` para atualizar os metadados visuais dos produtos demonstrativos. Instale as dependências e inicie backend e frontend seguindo o README.

No editor, **Acabamento do avatar → Humano** utiliza o rosto da referência. **Manequim neutro** permite escolher cabelo e cor. O cabelo do rosto fotográfico é fixo. Perfis anteriores podem escolher o novo acabamento no editor.

## O que mudou

- Camiseta e calça demonstrativas têm textura e dobras dos anexos, com recortes próprios para cada gênero.
- Cores das variantes são projetadas sobre o tecido, mantendo suas variações de luz; estampas continuam como camada independente.
- Largura/comprimento e caimento continuam variando por tamanho sobre o mesmo corpo.
- Peça isolada mantém apenas a peça escolhida, cueca ou calcinha/top neutros. Look completo continua independente por região.
- SVGs das roupas incluem o PNG internamente para funcionar também no build, sem referências externas bloqueadas pelo navegador.

## Limites desta versão

A composição é frontal 2D: rosto fotográfico, corpo-base estilizado e roupa texturizada. Não reproduz integralmente o corpo fotográfico do exemplo nem simula física do tecido. Alterar caimento estica a camada; não cria novas dobras fisicamente corretas. Cores são aproximações. Outras categorias usam os renderizadores anteriores até receberem seus próprios assets preparados. Uma foto enviada pelo usuário continua configurando proporções aproximadas, não reconstruindo rosto ou identidade.

## Verificação

Testes do fluxo real incluem perfil, foto e edição, gênero, tamanhos, caimento, estampas, modos, sacola e persistência. Veja as capturas atualizadas em docs/screenshots.
