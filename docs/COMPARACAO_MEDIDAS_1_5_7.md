# VesteIA 1.5.7 — comparação visual por medidas (experimental)

## Atualizar o projeto que já está aberto

1. Faça uma cópia da pasta atual como backup.
2. Baixe `VesteIA_Atualizacao_Medidas_1_5_7.zip` e extraia em uma pasta temporária.
3. Copie a pasta `frontend/src/features/fitting` do pacote para a mesma pasta do projeto atual, aceitando substituir os arquivos de mesmo nome. O pacote contém apenas os arquivos alterados/novos; conserve os demais.
4. O frontend iniciado com `npm run dev` atualiza automaticamente. Atualize a página com Ctrl+F5. Se estiver usando uma versão compilada, execute `npm run build` e publique o novo `dist`.
5. Backend, banco, dependências e `.env` continuam os mesmos. Esta atualização não exige recriar o banco nem instalar pacotes.

O ZIP completo é uma alternativa para quem prefere abrir uma cópia nova. Preserve seu `.env` e use seu banco atual.

## O que foi implementado

Na página do produto existe o painel **Comparar a imagem vestida pelas medidas**. Ele recebe os tamanhos/medidas da mesma API de catálogo usada pelo provador e altera somente um recorte da peça, sobre uma base fixa. Selecionar P/M/G/GG nesse painel sincroniza a seleção com o restante do provador e a sacola. Não há outra chamada de IA na troca de tamanho.

Largura, comprimento, manga e ombros têm proporções independentes. Para largura, usa primeiro `largura_cm`; quando ausente, admite metade de `torax_cm` (superiores) ou de `quadril_cm`/`cintura_cm` (inferiores). A convenção de medidas deve ser consistente entre tamanhos: largura plana de frente e circunferência completa são coisas diferentes. Não compara silenciosamente campos de definições diferentes. O modo exige largura e comprimento nos dois tamanhos e bloqueia razões fora de 0,65 a 1,50. Manga/ombros ausentes permanecem sem ajuste, explicitamente indicados.

## Preparar uma referência de verdade

1. Abra **Prévia realista com IA**, escolha Meu avatar e use **Salvar base do avatar para teste externo**. Isso funciona mesmo com IA não configurada.
2. Use a base num gerador externo ou uma produção de imagens que forneça a peça vestida. A configuração paga do Google foi preservada, mas não é necessária para importar uma imagem.
3. Tenha a mesma pose, proporções do corpo, resolução e enquadramento nas imagens da base e da peça vestida. A base precisa estar sem a peça, com cobertura íntima neutra. Alterações de corpo/pose geradas pela IA precisam ser corrigidas na preparação; o recorte não corrige esses erros. Um simples redimensionamento pode dar dimensões iguais sem alinhar o corpo.
4. Conheça o tamanho/medidas que a referência representa. A camiseta do nosso teste não tem tamanho comprovado; não se deve afirmar que é P ou M real.
5. Envie as duas imagens no novo painel. Selecione o tamanho conhecido da referência. Arraste os pontos para contornar só a roupa: exclua pescoço, braços, pele, fundo. Confirme o recorte/alinhamento.
6. Escolha outros tamanhos. Veja os valores vindos da API na tabela e salve a prévia se desejar. Editar o contorno invalida a confirmação anterior. As imagens importadas ficam apenas na página e se perdem ao fechá-la.

## Carregar uma referência automaticamente pelo catálogo

O esquema existente já aceita metadados JSON. Não é necessária migração. Uma loja pode preparar a referência uma vez por variante e corpo-base e colocar em `variant.metadata.visual.previa_medidas`:

```json
{
  "base_url": "/assets/referencias/SKU-base.png",
  "vestida_url": "/assets/referencias/SKU-M.png",
  "tamanho_referencia": "M",
  "calibrado": true,
  "contorno": [[0.44,0.20],[0.56,0.20],[0.68,0.25],[0.72,0.35],[0.62,0.37],[0.60,0.49],[0.40,0.49],[0.38,0.37],[0.28,0.35],[0.32,0.25]]
}
```

Os pontos acima são apenas um exemplo, não um recorte aprovado para qualquer peça. Coordenadas normalizadas 0 a 1, de 3 a 40 pontos em ordem no contorno. O tamanho precisa existir na variante. A confirmação `calibrado` significa que a loja verificou recorte, alinhamento e tamanho da referência. URLs externas precisam permitir CORS e devolver PNG/JPEG/WebP até 7 MB. A leitura de imagens não envia credenciais.

No PostgreSQL, a tabela deste projeto é `catalog_variants` e suas medidas ficam em `catalog_sizes.medidas` (JSONB). A API/importador já conserva os metadados. Exemplo não destrutivo, para adaptar ao SKU real:

```sql
UPDATE catalog_variants
SET metadata = metadata || jsonb_build_object(
  'visual', COALESCE(metadata->'visual', '{}'::jsonb) || jsonb_build_object(
    'previa_medidas', '<JSON completo da referência validada>'::jsonb
  )
)
WHERE sku = 'SKU_REAL_DA_VARIANTE';
```

Não execute o exemplo sem substituir os placeholders. A base importada é um corpo específico. Para outro avatar, prepare outra referência: este modo não transfere automaticamente a roupa realista entre corpos. Os renderizadores anteriores e a recomendação por medidas corporais informadas continuam disponíveis.

## O que ainda não foi implementado

Não é um novo modelo de IA treinado/condicionado em centímetros, não faz segmentação automática e não simula dobras, tecido, tensão ou folga física. É uma comparação gráfica relativa calibrada. A ampliação também transforma o desenho/estampa dentro do recorte; não restaura uma marca que a IA já tenha escrito errado. Resultados extremos podem continuar artificiais. Não há validação comercial de caimento ou centímetros por pixel.

A geração automática realista para cada tamanho respeitando centímetros exige um modelo/fluxo que aceite esses controles e sua validação; não basta repassar `tamanho=G` ao modelo que testamos. Nenhuma geração externa real foi executada nesta atualização. O painel pago anterior permanece independente.

## Prévia sem extrair

Abra `VesteIA_Previa_Medidas.html` no navegador. É uma demonstração independente com sua imagem e a tabela fictícia FORMA. A atribuição de P à imagem é ilustrativa, não uma medida real conhecida. Os botões mostram o mecanismo da comparação; o recorte e a base usados nessa demonstração precisam de preparação melhor para produção. Não depende de backend nem envia imagens.

## Validação

Build e ESLint: sem erros (dois avisos anteriores em LegacyProvador).
Teste unitário: razões de medidas, campos inválidos/faltantes, convenções incompatíveis, âncora fixa, limite de variação.
Teste navegador: roupa muda, pixels fora dela permanecem iguais em fixture controlada, troca sem chamada IA, bloqueio de resoluções diferentes, recorte invalida confirmação, layout móvel.
Regressões navegador: painel de IA e integração de loja com seleção G. API simulada nos testes; seu PostgreSQL e uma geração externa real não foram testados neste ambiente. Não foram necessários ajustes no backend.
