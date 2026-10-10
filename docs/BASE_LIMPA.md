# VesteIA 1.5.3 — peça selecionada e base limpa

A seleção substitui a roupa esportiva incorporada ao avatar por uma superfície lisa de manequim. Camiseta deixa as pernas livres; calça deixa o tronco livre; as demais categorias seguem a mesma regra. Mantém-se somente uma cobertura íntima neutra (cueca/calcinha e faixa no modelo feminino).

- Peça isolada: mostra somente a peça do catálogo selecionada.
- Look completo: mantém as peças que você adicionou explicitamente ao look.
- Base neutra: volta à base anterior, sem experimentar peças.
- Pele, cabelo, gênero, tamanhos, catálogo e abas continuam disponíveis.

## Atualização
Se já usa a 1.5.2, esta mudança está no frontend. Pare o terminal do frontend com Ctrl+C, substitua a pasta frontend pela deste ZIP (preserve qualquer configuração própria em .env), e execute nessa pasta:

```powershell
npm ci
npm run dev
```

Mantenha seu backend e seu banco atuais. Não é necessário executar SQL novo para essa correção. O ZIP também contém o projeto completo para instalação em pasta nova. Nesse caso, copie seu backend/.env para a nova pasta e siga docs/PERSONALIZACAO_HUMANA.md (Python 3.12). Não compartilhe sua senha.

## Limites visuais
As regiões livres agora são uma superfície sintética lisa, combinada com o rosto/cabelo da base humana. Não são uma reconstrução fotográfica do corpo. O caimento permanece uma simulação 2D; não equivale a prova física ou ajuste perfeito. A imagem real de cada produto depende dos recursos do catálogo.

## Implementação e validação
AvatarView ativa a base limpa quando há peças selecionadas. HumanAvatarBody combina a cabeça personalizada com a superfície do manequim. SmoothAvatarBody usa a mesma base normalizada para o modelo neutro. A cobertura íntima fica abaixo das peças do catálogo.

Novo recurso: frontend/public/assets/manequins-base-lisa.png, gerado como dois manequins artificiais de plástico cinza, masculino/feminino, vista frontal, superfície lisa, sem anatomia íntima, fundo transparente. O recorte e a recoloração são locais no navegador.

Build passou. ESLint: zero erros; dois avisos preexistentes em LegacyProvador. Testes de base, personalização e visuais passaram com API simulada. O teste de base cobre sete categorias x dois gêneros, restauração da base, look explícito e manequim neutro. Backend/PostgreSQL não foram retestados nesta mudança de renderização.

As PNGs entregues são capturas da aplicação com produtos demonstrativos, não montagens externas.
