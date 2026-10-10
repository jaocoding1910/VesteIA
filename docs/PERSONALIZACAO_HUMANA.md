# VesteIA 1.5.2 — personalização humana

Base: ZIP VesteIA_1_5_Abas_e_Look(1).zip enviado pelo usuário. Esta entrega é uma evolução da versão 2D aprovada; não inclui o experimento rotacional 3D da 1.6.

## Alterações
- Avatares humanos masculino e feminino: pele, cabelo raspado, curto liso, crespo/afro curto, longo liso e cor do cabelo.
- Atlas fotográficos locais com quatro estilos por gênero, processados no navegador. Não envia imagens para serviços externos para personalizar.
- Recoloração baseada em pixels de pele, preservando roupa neutra cinza. Cores de cabelo ajustadas na região da cabeça.
- Perfil aceita `crespo` na API; escolhas usam o fluxo existente de salvamento e armazenamento local.
- Nas imagens demonstrativas de roupa, o filtro remove os pixels residuais de pele do modelo fotografado para não deixar gola e mangas presas à pele clara original. Esse filtro não é aplicado a fotografias arbitrárias do catálogo.
- Roupa recebe uma base opaca no molde para reduzir vazamentos de pele, e a imagem é recortada pelo contorno da categoria antes de deformar.
- Foto como referência, abas, catálogo, tamanhos e regras de look preservados.

## Atualizar no Windows
1. Extraia o ZIP em uma pasta nova e abra a pasta vesteia no VS Code.
2. Copie seu backend/.env atual para o backend novo, sem compartilhar a senha.
3. No terminal backend, crie ambiente Python 3.12, instale e inicie:

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\python.exe -m pip install -r requirements.txt
.\.venv312\Scripts\python.exe -m uvicorn app.main:app --reload
```

Usando o mesmo banco já configurado, não precisa apagar dados nem executar SQL novo.
4. Segundo terminal, dentro de frontend:

```powershell
npm install
npm run dev
```

5. Abra o endereço Local. Clique em Editar meu avatar ou Criar meu avatar, escolha Humano, modelo, pele e cabelo. Clique em Salvar meu avatar.
6. Reinicie o backend atualizado para que a opção crespo seja aceita. Usar o frontend novo com backend antigo pode gerar HTTP 422 nessa opção.

## Limites
É um provador frontal 2D aproximado. Bases de corpo foram renovadas para comportar os cabelos e mantêm roupas esportivas neutras como cobertura. A base masculina usa bermuda esportiva mais longa. O rosto permanece da base; mudar pele não representa automaticamente todos os traços de uma etnia. Recoloração de imagem não substitui diferentes fotografias para cada tom, e pode ter pequenos artefatos em áreas de sombra. O cabelo longo permanece próximo dos ombros. Não há reconstrução fotográfica individual ou simulação física de tecidos. A alteração de caimento reforça opacidade e recorte, não garante vestibilidade exata.

## Validação
Build e lint, testes de modelo/malha/look, teste visual das sete categorias e teste de navegador para dois gêneros, quatro cabelos, pele/cabelo, salvar/recarregar e mobile. Testes de navegador usam API simulada. Contrato Pydantic Profile validado para os quatro estilos nos dois gêneros; não executada nova integração PostgreSQL nesta alteração.

Assets criados com geração de imagens: atlas 2x2 com o mesmo adulto em pose frontal, quatro cabelos, roupas esportivas opacas, fundo transparente. Feminino usou a base enviada no projeto como referência; masculino foi gerado como manequim esportivo. A primeira tentativa masculina foi bloqueada; a segunda usou bermuda longa.
