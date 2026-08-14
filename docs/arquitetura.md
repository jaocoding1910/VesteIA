---

## 7. Arquitetura atual do backend

O backend do VesteIA utiliza uma arquitetura organizada por responsabilidades.

### API

Responsável por receber as requisições HTTP e disponibilizar os endpoints da aplicação.

Arquivo principal:

- `app/api/routes.py`

Principais funcionalidades disponíveis atualmente:

- cadastro de produtos;
- listagem de produtos;
- busca de produto por ID;
- atualização de produtos;
- exclusão de produtos;
- filtros de catálogo;
- gerenciamento temporário do perfil do usuário;
- recomendação de tamanho;
- recomendação de produtos.

### Services

Responsáveis pelas regras de negócio e acesso aos dados.

#### `catalogo.py`

Responsável pelas operações relacionadas ao catálogo e ao banco de dados:

- listar produtos;
- buscar produtos;
- adicionar produtos;
- atualizar produtos;
- excluir produtos;
- filtrar produtos por características.

#### `recomendacao.py`

Responsável pelas regras do sistema de recomendação:

- calcular tamanho recomendado;
- considerar altura, peso e cintura;
- considerar preferência de caimento;
- analisar características da peça;
- gerar observações sobre o possível caimento.

### Schemas

Os schemas Pydantic são responsáveis pela validação e estrutura dos dados recebidos e retornados pela API.

### Models

Representam as entidades utilizadas internamente pela aplicação.

### Database

A aplicação utiliza PostgreSQL para persistência dos produtos do catálogo.

---

## 8. Fluxo atual de recomendação

O fluxo atual do motor de recomendação funciona da seguinte maneira:

1. O usuário informa altura, peso e opcionalmente cintura.
2. O usuário pode informar uma preferência de caimento.
3. O sistema calcula um tamanho recomendado.
4. O catálogo é consultado utilizando o tamanho calculado e outros filtros opcionais.
5. Os produtos compatíveis são analisados.
6. O sistema retorna:
   - tamanho recomendado;
   - produtos encontrados;
   - características das peças;
   - observações sobre o possível caimento.

Caso altura e peso não sejam enviados diretamente, o sistema poderá utilizar os dados armazenados temporariamente no perfil do usuário.

---

## 9. Tecnologias utilizadas

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

### Banco de dados

- PostgreSQL
- psycopg2

### Documentação e testes da API

- Swagger / OpenAPI

---

## 10. Estrutura simplificada

VesteIA
│
├── backend
│   └── app
│       ├── api
│       │   └── routes.py
│       ├── database
│       │   └── database.py
│       ├── models
│       │   └── produto.py
│       ├── schemas
│       │   └── produto_schema.py
│       ├── services
│       │   ├── catalogo.py
│       │   └── recomendacao.py
│       ├── perfil.py
│       └── main.py
│
└── arquitetura.md

---

## 11. Estado atual do MVP

O backend já possui uma base funcional para gerenciamento do catálogo e recomendação de produtos.

Atualmente estão implementados:

- API REST com FastAPI;
- integração com PostgreSQL;
- CRUD de produtos;
- filtros dinâmicos de catálogo;
- perfil temporário do usuário;
- recomendação de tamanho;
- preferência de caimento;
- recomendação de produtos;
- análise básica das características da peça.

A geração visual do provador virtual com foto ou avatar pertence às próximas etapas de evolução do projeto.

---

## 12. Evoluções futuras

Entre as próximas evoluções planejadas estão:

- persistência dos perfis dos usuários no banco de dados;
- autenticação de usuários;
- tabelas de medidas específicas por produto ou marca;
- melhoria do motor de recomendação;
- integração com o frontend;
- processamento de imagens;
- geração do provador virtual;
- criação de avatar;
- comparação visual de produtos;
- integração com plataformas de comércio eletrônico.