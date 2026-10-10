# Onde manter cada parte

| Mudança | Arquivo/camada |
| --- | --- |
| Paleta/layout/responsividade | frontend/src/Experience.css |
| Cabeçalho/nav/rotas | frontend/src/App.jsx |
| Cartões, categorias/filtros | features/catalog/Catalog.jsx e catalogModel.js |
| Produto, tamanhos, seleção | features/fitting/FittingRoom.jsx |
| Perfil e apresentação | features/profile/ProfileEditor.jsx |
| Estado local de sacola/look/favoritos | features/commerce/Store.jsx |
| Validação comercial no servidor | backend/app/api/mvp.py |
| Cadastro/API de catálogo | repositories/catalog_repository.py |
| Catálogo externo | adapters/catalog_adapter.py e scripts/import_catalog.py |
| Dados de exemplo | scripts/setup_db.py, somente IDs demo-* |
| Categoria estrutural | services/categorias_vestuario.py |
| Regras de comparação medidas | services/comparacao_mvp.py |
| Recomendação foto anterior | services/recomendacao_tamanho_provador.py; não confundir com a comparação declarada |
| Transporte HTTP | services/mvpApi.js e provadorService.js |
| Arte natural / alternativa ilustrada | features/fitting/AvatarView.jsx / AvatarIllustration.jsx |
| Geometria por foto | AvatarRenderer2D.jsx + components/vestimentas |
| Upload/processamento | api/provador.py e services/processamento_imagem.py |
| Detecção/qualidade | services/deteccao_pessoa.py e qualidade_captura.py |
| Tokens/expiração | services/photo_privacy.py e middleware main.py |
| Futuro serviço gerador | services/generated_tryon.py |
| Persistência estrutural | backend/migrations, sempre evolução aditiva |

Ao adicionar categoria, defina o contrato de medidas e região, renderer correspondente, fixtures e razões de comparação. A grade vem do fornecedor: evite uma enumeração universal no frontend. Não use raça, pele, cabelo ou foto monocular para inventar medidas.

As dimensões do corpo não mudam quando se troca o tamanho de uma peça. O renderer recebe apenas a variante/tabela e transforma sua camada de vestimenta. A ordenação normalizada usa sort_order; rótulos nacionais/internacionais permanecem como foram cadastrados.

A camada de recomendação retorna motivos e confiança; a interface não replica suas regras. O renderer não recomenda tamanho. Foto/landmarks, medidas declaradas e imagem artística são origens diferentes e devem continuar distintas.

Para publicar: planeje hospedagem Python/PostgreSQL e uma origem HTTPS para Vite; configure CORS, acesso administrativo, autenticação, rate limiting, logs, retenção/limpeza e armazenamento privado. O CRUD histórico foi preservado para desenvolvimento e ainda exige controles de acesso antes de exposição pública.
