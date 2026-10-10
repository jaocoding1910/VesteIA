# Arquivos alterados — VesteIA 1.5.8 → 2.0

A = adicionado · M = modificado · D = removido. Gerado com `git diff --name-status original mvp-provador`.

```
M	.gitignore
M	INICIAR_BACKEND.bat
M	LEIA_PRIMEIRO.md
M	README.md
A	backend/.env.example
A	backend/app/config.py
A	backend/app/logging_safe.py
M	backend/app/main.py
A	backend/app/studio/__init__.py
A	backend/app/studio/api.py
A	backend/app/studio/categories.py
A	backend/app/studio/credits.py
A	backend/app/studio/images.py
A	backend/app/studio/providers/__init__.py
A	backend/app/studio/providers/base.py
A	backend/app/studio/providers/local.py
A	backend/app/studio/providers/mock.py
A	backend/app/studio/providers/openai_images.py
A	backend/app/studio/sessions.py
A	backend/app/studio/sizes.py
A	backend/app/studio/usage.py
A	backend/requirements-legacy.txt
M	backend/requirements.txt
A	backend/scripts/limpeza_catalogo/1_inventario.sql
A	backend/scripts/limpeza_catalogo/2_backup.ps1
A	backend/scripts/limpeza_catalogo/3_remover_demo.sql
A	backend/scripts/limpeza_catalogo/LEIA.md
A	backend/tests/test_studio.py
A	docs/PROVADOR_2_0.md
A	docs/RELATORIO_TESTES_2_0.md
M	frontend/.env.example
M	frontend/index.html
M	frontend/package.json
A	frontend/public/assets/brand/vesteia-mark.png
A	frontend/public/assets/experience/apresentacao-capa.webp
A	frontend/public/assets/experience/avatar-base-sm.webp
D	frontend/public/assets/experience/avatar-base.png
A	frontend/public/assets/experience/avatar-base.webp
D	frontend/public/assets/experience/camiseta-branca.png
A	frontend/public/assets/experience/camiseta-branca.webp
D	frontend/public/assets/experience/camiseta-preta.png
A	frontend/public/assets/experience/camiseta-preta.webp
A	frontend/public/assets/experience/look-branco-sm.webp
D	frontend/public/assets/experience/look-branco.png
A	frontend/public/assets/experience/look-branco.webp
A	frontend/public/assets/experience/look-preto-sm.webp
D	frontend/public/assets/experience/look-preto.png
A	frontend/public/assets/experience/look-preto.webp
D	frontend/public/assets/experience/tamanhos-branco.png
A	frontend/public/assets/experience/tamanhos-branco.webp
D	frontend/public/assets/experience/tamanhos-preto.png
A	frontend/public/assets/experience/tamanhos-preto.webp
A	frontend/public/favicon.png
M	frontend/src/App.jsx
A	frontend/src/Layout.css
M	frontend/src/components/ui/Icon.jsx
A	frontend/src/components/ui/useReveal.js
M	frontend/src/features/home/HomePage.css
M	frontend/src/features/home/HomePage.jsx
A	frontend/src/features/studio/CompareStep.jsx
A	frontend/src/features/studio/GenerateSteps.jsx
A	frontend/src/features/studio/InputSteps.jsx
A	frontend/src/features/studio/Studio.css
A	frontend/src/features/studio/StudioPage.jsx
A	frontend/src/features/studio/api.js
A	frontend/src/features/studio/demoBackend.js
A	frontend/src/features/studio/errors.js
A	frontend/src/features/studio/files.js
A	frontend/src/features/studio/sizeModel.js
A	frontend/src/features/studio/ui.jsx
M	frontend/src/index.css
A	frontend/tests/fixtures/calca-teste.png
A	frontend/tests/fixtures/nao-imagem.jpg
A	frontend/tests/studio-e2e.mjs
```

Não incluídos no ZIP: backend/.env (credenciais), backend/.venv312, frontend/node_modules, backend/data.
Arquivos legados do frontend (catálogo, loja, provador 2D) continuam no projeto, mas não são mais carregados pela interface.
