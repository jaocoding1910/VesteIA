-- Somente leitura. Mostra o que 3_remover_demo.sql afetaria.
WITH alvo AS (
  SELECT id FROM catalog_products
  WHERE external_product_id LIKE 'forma-demo-%' OR external_product_id LIKE 'demo-%'
     OR NULLIF(metadata->>'loja_demo', '') IS NOT NULL
)
SELECT p.id, p.external_product_id, p.nome, p.categoria,
       (SELECT COUNT(*) FROM catalog_variants v WHERE v.product_id = p.id) AS variantes,
       (SELECT COUNT(*) FROM catalog_sizes s JOIN catalog_variants v ON v.id = s.variant_id WHERE v.product_id = p.id) AS tamanhos
FROM catalog_products p JOIN alvo a ON a.id = p.id ORDER BY p.id;

SELECT (SELECT COUNT(*) FROM catalog_products) AS produtos_total,
       (SELECT COUNT(*) FROM catalog_products WHERE external_product_id LIKE 'forma-demo-%' OR external_product_id LIKE 'demo-%'
          OR NULLIF(metadata->>'loja_demo', '') IS NOT NULL) AS produtos_demo;
