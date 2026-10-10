# Abrir o VesteIA 1.5.4

Esta versão atualiza frontend e backend (novos caimentos Slim/Amplo). Não atualize só o frontend: o backend anterior pode rejeitar esses valores com HTTP 422.

1. Pare os dois terminais com Ctrl+C e extraia o ZIP em uma pasta nova.
2. Abra a pasta vesteia no VS Code.
3. Copie seu backend/.env da versão que funciona para o backend novo. Se usa frontend/.env próprio, copie-o também. Mantenha o mesmo banco PostgreSQL. Nenhuma senha acompanha o ZIP.
4. Primeiro terminal, a partir da pasta vesteia:

```powershell
cd backend
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
.\.venv312\Scripts\python.exe -m uvicorn app.main:app --reload
```

Não precisa ativar o venv: os comandos já usam seu Python diretamente. Aguarde “Application startup complete”. Não rode na pasta vesteia; o Uvicorn deve ser executado dentro de backend.

5. Segundo terminal, também a partir da pasta vesteia:

```powershell
cd frontend
npm ci
npm run dev
```

6. Abra o endereço Local mostrado pelo Vite. Suas escolhas no mesmo navegador/origem continuam no armazenamento local. Se o Vite usar outra porta, seu perfil local pode não aparecer; prefira a porta anterior.

Não precisa apagar banco, executar SQL novo ou rodar seed para esta atualização sobre a 1.5.3. Para primeira instalação, siga o README original e suas instruções de banco.

Para testes do frontend: npm run test:premium e os demais scripts package.json. Para testes do backend: instale requirements.txt e requirements-test.txt; execute python -m pytest tests/test_finalizacao.py tests/test_premium.py -q dentro de backend. Testes de PostgreSQL exigem banco isolado com nome terminado em _test.

Leia docs/PREMIUM_1_5_4.md para alterações, limites e validação. Não remova sua versão anterior até conferir a nova no seu ambiente.
