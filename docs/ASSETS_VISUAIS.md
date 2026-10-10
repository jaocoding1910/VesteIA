# Bases visuais

Os dois PNGs em `frontend/public/assets/avatar-*-natural.png` foram gerados com a habilidade imagegen e a ferramenta integrada, para este projeto. São modelos artísticos genéricos; não são fotos do usuário nem resultados individualizados de prova virtual.

Prompt masculino: modelo masculino adulto, pele média, cabelo curto escuro, pose frontal simétrica, camiseta preta sem marca, calça preta reta, tênis off-white, corpo inteiro, luz suave, fundo transparente, aspecto editorial natural.
Prompt feminino: modelo feminino adulto, pele média, cabelo bob escuro, mesma pose frontal, camiseta preta, calça preta e tênis off-white, corpo inteiro, luz suave, fundo transparente.

O recorte por camadas SVG em `AvatarView.jsx` elimina o halo das artes, mantém a base corporal e altera a camada da camiseta conforme largura/comprimento da variante. Essa transformação é uma composição 2D aproximada, sem colisão, tecido físico ou calibração antropométrica.

Para outras cores/categorias, combinação de look ou aparência personalizada, o adaptador usa `AvatarIllustration.jsx`, uma ilustração vetorial dinâmica. A escolha “Ilustrado” também permite ativá-la diretamente. AvatarRenderer2D e AvatarRenderer3D anteriores foram preservados; o primeiro é usado no fluxo de fotografia. O segundo continua acessível no provador original, mas seu nome histórico não significa que haja uma cena WebGL.

A camiseta de produto existente no ZIP foi preservada. Peças sem imagem cadastrada usam ilustrações vetoriais explícitas; importações externas podem fornecer `imagem_url` de catálogo.


## Bases neutras atuais

frontend/public/assets/manequim-masculino-base.png e manequim-feminino-base.png: imagens geradas pelo recurso integrado de criação de imagens, PNG RGBA 1024×1536 com transparência, usadas no Ilustrado.

Prompt masculino: manequim adulto de varejo 3D estilizado, plástico cinza fosco, cabeça sem rosto, cueca boxer opaca cinza-escura, frente/corpo inteiro, braços separados levemente do torso, pés sem calçado, fundo transparente.
Prompt feminino: mesmo padrão de manequim, proporções adultas femininas, calcinha de cobertura integral e faixa opaca no busto, frente/corpo inteiro, fundo transparente.

O renderer não modifica esses arquivos ao trocar tamanho. A geometria e arte da roupa vêm do SKU e são sobrepostas. Assets antigos foram preservados para compatibilidade do provador legado e do teste de foto.
