ALTER TABLE catalog_sizes ADD COLUMN IF NOT EXISTS legacy_product_id BIGINT REFERENCES produtos(id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_size_legacy ON catalog_sizes(legacy_product_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_external_unique ON catalog_products(external_product_id) WHERE external_product_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_variant_sku ON catalog_variants(sku) WHERE sku IS NOT NULL;
CREATE TABLE IF NOT EXISTS client_profiles (
 id UUID PRIMARY KEY, apelido VARCHAR(60) NOT NULL, perfil JSONB NOT NULL DEFAULT '{}'::jsonb,
 updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS sessoes_provador (
 id BIGSERIAL PRIMARY KEY, produto_id BIGINT NOT NULL, produto_nome TEXT NOT NULL,
 tamanho VARCHAR(30), modo VARCHAR(20) NOT NULL, nome_arquivo TEXT NOT NULL,
 tipo_arquivo VARCHAR(100) NOT NULL, tamanho_bytes BIGINT NOT NULL, status VARCHAR(50) NOT NULL,
 caminho_arquivo TEXT, caminho_normalizado TEXT, criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE sessoes_provador ADD COLUMN IF NOT EXISTS access_token TEXT;
ALTER TABLE sessoes_provador ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ;
