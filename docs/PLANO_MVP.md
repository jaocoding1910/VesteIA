# Evolução do MVP — 30/09/2026

Auditoria anterior a alterações: 69 arquivos de código/configuração/documentação; análise sintática de todos os módulos Python, imports, funções e contratos em auditoria-fontes.json. A imagem e o escopo enviados orientam esta entrega.

## Diagnóstico
- FastAPI preserva CRUD legado, catálogo por variante, sessões foto-first e pipeline das sprints 48–53.
- Serviços separavam captura, landmarks, calibração, contrato, geometria e recomendação; não devem ser fundidos.
- React tinha App.jsx com 3.979 linhas e CSS com mais de 80 KB. Interface era formulário técnico, sem navegação comercial completa.
- AvatarRenderer3D é um humanoide em HTML/CSS: não há WebGL, malha 3D ou rotação física. Será identificado como visualização 2D.
- AvatarRenderer2D e seis renderers de vestimenta consomem contratos normalizados; permanecem disponíveis no fluxo de fotografia.
- Migration normalizada existia, mas não era consumida. Não havia inicialização reproduzível do banco nem seed completo.
- Perfil legado é global/em memória. Nova experiência usa perfil anônimo persistido separadamente; não altera seus endpoints.
- Upload aceitava MIME e tamanho, mas precisava validação de conteúdo, limite antes da leitura completa, expiração e exclusão.
- Recomendação visual do avatar não considera medidas reais de corpo e não deve ser apresentada como ajuste físico.

## Plano aprovado pelo escopo
1. Migrar de forma aditiva, ligar catálogo normalizado ao legado por ID de SKU e fornecer importador externo e seed idempotente.
2. Nova experiência React modular: loja, produto, onboarding, comparação dinâmica, medidas declaradas, favoritos, carrinho e look.
3. Manter API/serviços/renderers anteriores; separar comparação baseada em medidas declaradas de transformação visual aproximada.
4. Reproduzir composição escura/ciano/violeta da referência, comparação simultânea desktop e seleção focada mobile.
5. Integrar fotos ao pipeline real com qualidade/landmarks e fallback explícito. Sem centímetros inferidos automaticamente.
6. Validar contratos, migrations/seed, interface em desktop/mobile, erros, persistência e documentação.

## Fronteiras
Pagamento, autenticação comercial, integração live de uma plataforma específica, simulação física e geração fotorrealista por IA requerem serviços/credenciais próprios. O MVP entrega adaptadores e limites explícitos.
