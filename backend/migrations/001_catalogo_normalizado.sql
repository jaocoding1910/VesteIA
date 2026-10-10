-- VesteIA MVP 1.0 — evolução não destrutiva do catálogo.
-- Não remove nem altera a tabela legada `produtos`.
-- Execute manualmente após backup. Pode ser executado novamente com segurança estrutural.

CREATE TABLE IF NOT EXISTS catalog_products (
  id BIGSERIAL PRIMARY KEY,
  external_product_id VARCHAR(255),
  nome VARCHAR(255) NOT NULL,
  categoria VARCHAR(100) NOT NULL,
  marca VARCHAR(120),
  descricao TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS catalog_variants (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL REFERENCES catalog_products(id) ON DELETE CASCADE,
  sku VARCHAR(120),
  cor VARCHAR(100),
  modelagem VARCHAR(80),
  preco NUMERIC(10,2),
  imagem_url TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS catalog_sizes (
  id BIGSERIAL PRIMARY KEY,
  variant_id BIGINT NOT NULL REFERENCES catalog_variants(id) ON DELETE CASCADE,
  label VARCHAR(30) NOT NULL,
  sort_order INTEGER NOT NULL DEFAULT 0,
  estoque INTEGER,
  medidas JSONB NOT NULL DEFAULT '{}'::jsonb,
  UNIQUE (variant_id, label)
);

CREATE INDEX IF NOT EXISTS idx_catalog_variants_product ON catalog_variants(product_id);
CREATE INDEX IF NOT EXISTS idx_catalog_sizes_variant ON catalog_sizes(variant_id);
CREATE INDEX IF NOT EXISTS idx_catalog_products_external ON catalog_products(external_product_id);
