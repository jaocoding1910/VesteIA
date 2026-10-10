-- Remove SOMENTE produtos de demonstração do catálogo normalizado.
-- Faça o backup (2_backup.ps1) antes. Termina em ROLLBACK de propósito:
-- confira as contagens e troque a última linha por COMMIT para efetivar.
BEGIN;

CREATE TEMP TABLE alvo ON COMMIT DROP AS
  SELECT id FROM catalog_products
  WHERE external_product_id LIKE 'forma-demo-%' OR external_product_id LIKE 'demo-%'
     OR NULLIF(metadata->>'loja_demo', '') IS NOT NULL;

SELECT COUNT(*) AS produtos_a_remover FROM alvo;
SELECT COUNT(*) AS variantes_a_remover FROM catalog_variants WHERE product_id IN (SELECT id FROM alvo);
SELECT COUNT(*) AS tamanhos_a_remover FROM catalog_sizes WHERE variant_id IN
  (SELECT id FROM catalog_variants WHERE product_id IN (SELECT id FROM alvo));

DELETE FROM catalog_products WHERE id IN (SELECT id FROM alvo);  -- variantes e tamanhos saem por CASCADE

ROLLBACK;  -- troque por COMMIT somente depois de conferir
