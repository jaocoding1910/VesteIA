# VesteIA 1.5 — abas do avatar e regras do look

## Instalar e ver todas as categorias
Extraia o projeto inteiro em pasta nova, configure backend/.env e siga o README para instalar as dependências. Do terminal na pasta backend, execute:

```powershell
python scripts/setup_db.py --seed-all
python -m uvicorn app.main:app --reload
```

No outro terminal, na pasta frontend, execute `npm install` e `npm run dev`. O comando `--seed-all` adiciona/atualiza sete produtos demonstrativos no PostgreSQL, preservando os produtos existentes. `--seed` continua carregando apenas camiseta e calça para compatibilidade com a demonstração anterior.

## Novas funções
- Abas **Visual natural** e **Pontos e proporções** na página do provador e no editor do avatar.
- Mesmo corpo, peças e tamanhos nas duas abas. A aba escolhida no provador é mantida na sessão ao trocar de produto.
- Pontos luminosos sobre o avatar, acompanhando as proporções gráficas do molde. São guias ilustrativos, não landmarks da foto nem centímetros medidos.
- Peça isolada: somente a seleção atual, com a cobertura neutra da base. Base neutra: nenhuma peça do catálogo. Look completo: todas as peças ativas e compatíveis.
- Adicionar peça de uma região ocupada substitui a peça anterior. Calça, bermuda e saia compartilham região inferior; vestido ocupa regiões superior e inferior; tênis e boné têm regiões próprias.
- Boné foi acrescentado ao catálogo, filtro, importação neutra e renderer frontal. Sem recomendação de tamanho com base em peso/altura.
- Perfil, favoritos, sacola, tamanho e caimento por item continuam disponíveis.

## Acabamento e limites
Camiseta/calça mantêm os assets preparados e a malha da versão 1.4. Bermuda, saia, vestido, tênis e boné têm renderizadores demonstrativos aproximados, não uma nova reconstrução fotográfica das peças. A regra de seleção/look funciona nas sete categorias, mas o acabamento fotográfico não está concluído para todas elas.

Os seis modelos enviados são referências visuais, não foram usados como imagens estáticas para fingir mudança de roupa/tamanho. As bases humanas existentes continuam nesta versão. Rosto/cabelo/pele no modo Humano ainda são fixos; o modo Manequim permite tom e cabelo. Uma biblioteca de rostos humanos diversos ainda precisa de assets e integração própria.

Novas peças de uma loja precisam das medidas e imagens preparadas/calibradas por variante descritas em ENCAIXE_POR_REGIOES.md. Nenhum banco conectado automaticamente garante encaixe perfeito ou extração fiel de uma foto arbitrária. O sistema continua uma aproximação frontal em 2D, sem simulação física de tecido.

## Verificações
Backend: 29 testes. Frontend: malha/modelo, regras de regiões, sete categorias, abas, editor, perfil/foto, look, persistência e mobile. Capturas `final-look-natural.png`, `final-look-pontos.png`, `final-saia-isolada.png`, `final-editor-pontos.png` e `final-mobile.png` foram feitas no navegador, com o catálogo PostgreSQL real para o fluxo final.
