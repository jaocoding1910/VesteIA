# Limpeza opcional do catálogo antigo (PostgreSQL)

**Não é necessária para o provador.** No modo padrão (`DATABASE_ENABLED=false`) o VesteIA não lê o banco,
então os produtos antigos simplesmente não aparecem. Use este procedimento somente se quiser religar o banco
legado (`DATABASE_ENABLED=true`) sem os produtos de demonstração.

Nada aqui roda automaticamente. Execute manualmente, na ordem, e leia cada saída.

1. **Inventário (somente leitura):** `1_inventario.sql` lista exatamente quais registros seriam afetados.
2. **Backup:** `2_backup.ps1` gera um arquivo `.dump` das tabelas do catálogo antes de qualquer alteração.
3. **Remoção:** `3_remover_demo.sql` apaga apenas produtos de demonstração (identificados por
   `external_product_id` começando com `forma-demo-` ou `demo-`, ou `metadata->>'loja_demo'` preenchido).
   Variantes e tamanhos ligados a eles saem junto (ON DELETE CASCADE).
   O script termina com `ROLLBACK`: confira as contagens e só troque para `COMMIT` se estiverem corretas.

O que **não** é alterado: a tabela legada `produtos`, `client_profiles`, `sessoes_provador` e qualquer produto
que não seja de demonstração. Não há `DROP`, `TRUNCATE` nem exclusão do banco.

Para restaurar o backup: `pg_restore --clean --data-only -h localhost -U SEU_USUARIO -d SEU_BANCO backup-catalogo-AAAAMMDD.dump`
