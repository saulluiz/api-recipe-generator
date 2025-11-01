# Arquitetura do Sistema - API Recipe Generator

## Visão Geral

O API Recipe Generator é um sistema backend desenvolvido para gerenciar e gerar receitas culinárias de forma inteligente. A aplicação oferece funcionalidades completas de CRUD para receitas, ingredientes e usuários, além de integração com inteligência artificial para geração automatizada de receitas baseadas em ingredientes disponíveis.

## Arquitetura da Aplicação

### Padrão Arquitetural

A aplicação segue o padrão de arquitetura em camadas (Layered Architecture), organizada da seguinte forma:

```
┌─────────────────────────────────────┐
│        Camada de Apresentação       │
│         (API REST/GraphQL)          │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│      Camada de Lógica de Negócio    │
│         (Business Logic)            │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│     Camada de Acesso a Dados        │
│        (Data Access Layer)          │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│        Camada de Persistência       │
│          (PostgreSQL)               │
└─────────────────────────────────────┘
```

### Estrutura de Diretórios

```
src/
├── api/
│   ├── routes/
│   │   ├── recipes.py
│   │   ├── ingredients.py
│   │   ├── users.py
│   │   └── ai_generator.py
│   ├── middlewares/
│   │   └── auth.py
│   └── schemas/
│       ├── recipe_schema.py
│       ├── ingredient_schema.py
│       └── user_schema.py
├── core/
│   ├── config.py
│   └── security.py
├── models/
│   ├── recipe.py
│   ├── ingredient.py
│   ├── user.py
│   └── recipe_ingredient.py
├── services/
│   ├── recipe_service.py
│   ├── ingredient_service.py
│   ├── user_service.py
│   └── ai_service.py
├── repositories/
│   ├── recipe_repository.py
│   ├── ingredient_repository.py
│   └── user_repository.py
└── database/
    ├── connection.py
    └── migrations/
```

## Stack Tecnológico

### Framework Web

**FastAPI 0.104+**

FastAPI foi escolhido como framework principal devido às seguintes características:

- Validação automática de dados através de type hints Python
- Documentação automática via OpenAPI (Swagger UI)
- Suporte nativo a operações assíncronas
- Tipagem estática que reduz erros em tempo de desenvolvimento
- Geração automática de schemas JSON

### Banco de Dados

**Supabase (PostgreSQL 15+)**

Supabase foi escolhido como plataforma de backend-as-a-service, fornecendo PostgreSQL gerenciado com recursos adicionais:

- PostgreSQL 15+ totalmente gerenciado e otimizado
- Backup automático e recuperação de desastres
- Escalabilidade automática de recursos
- Interface de administração web integrada
- APIs REST e GraphQL geradas automaticamente (opcionais)
- Autenticação e autorização integradas (opcionais)
- Storage para arquivos (imagens de receitas)
- Suporte a Row Level Security (RLS)
- Conexões pooling automáticas via PgBouncer
- Monitoramento e logs integrados

### ORM

**SQLAlchemy 2.0+**

SQLAlchemy atua como camada de abstração entre a aplicação e o banco de dados PostgreSQL do Supabase:

- Compatibilidade total com PostgreSQL do Supabase
- ORM completo com suporte a relacionamentos complexos
- Query builder type-safe
- Sistema de migrations através do Alembic
- Suporte a conexões assíncronas (async/await)
- Pool de conexões configurável
- Lazy loading e eager loading de relacionamentos
- Conexão via connection string do Supabase

### Validação e Serialização

**Pydantic 2.0+**

Pydantic é utilizado para validação de dados e serialização:

- Validação automática de dados em tempo de execução
- Conversão automática de tipos
- Geração de schemas JSON Schema
- Integração nativa com FastAPI
- Performance otimizada através de Rust (pydantic-core)

### Inteligência Artificial

**OpenAI API / Google Gemini API**

Integração com APIs de IA generativa para criação de receitas:

- Geração de receitas baseadas em ingredientes fornecidos
- Sugestões de substituições de ingredientes
- Adaptação de receitas para restrições alimentares
- Cálculo automático de porções e tempos de preparo

**LangChain**

Framework para orquestração de LLMs:

- Construção de chains de prompts estruturados
- Gerenciamento de contexto e memória
- Integração com múltiplos provedores de IA
- Templates reutilizáveis de prompts

### Autenticação

**JWT (JSON Web Tokens)**

Sistema de autenticação baseado em tokens:

- Tokens para identificação de usuários
- Payload com informações do usuário
- Expiração configurável

**Python-Jose**

Biblioteca para criação e validação de JWTs:

- Criação de tokens de autenticação
- Validação de tokens recebidos

### Gerenciamento de Ambiente

**Python-dotenv**

Carregamento de variáveis de ambiente:

- Separação de configurações por ambiente
- Proteção de credenciais sensíveis
- Fácil configuração em diferentes ambientes

### Documentação

**Swagger UI / ReDoc**

Documentação interativa da API:

- Interface web para testar endpoints
- Geração automática a partir do código
- Schemas de requisição e resposta
- Exemplos de uso

## Modelo de Dados

### Entidades Principais

#### User (Usuário)

```
- id: UUID (PK)
- username: String (unique, indexed)
- email: String (unique, indexed)
- password: String
- full_name: String
```

#### Recipe (Receita)

```
- id: UUID (PK)
- title: String (indexed)
- description: Text
- instructions: Text
- prep_time: Integer (minutos)
- cook_time: Integer (minutos)
- servings: Integer
- difficulty: Enum (fácil, médio, difícil)
- category: String (indexed)
- image_url: String (nullable)
- user_id: UUID (FK -> User)
```

#### Ingredient (Ingrediente)

```
- id: UUID (PK)
- name: String (unique, indexed)
- category: String (indexed)
```

#### RecipeIngredient (Relacionamento N:N)

```
- id: UUID (PK)
- recipe_id: UUID (FK -> Recipe)
- ingredient_id: UUID (FK -> Ingredient)
- quantity: Float
- unit: String
- notes: String (nullable)
```

### Relacionamentos

- Um usuário pode criar múltiplas receitas (1:N)
- Uma receita pertence a um usuário (N:1)
- Uma receita pode ter múltiplos ingredientes (N:N através de RecipeIngredient)
- Um ingrediente pode estar em múltiplas receitas (N:N através de RecipeIngredient)

### Índices

- Índices em campos de busca frequente: username, email, recipe.title, ingredient.name
- Índices compostos para queries complexas: (recipe.category, recipe.difficulty)
- Índices para foreign keys: recipe.user_id, recipe_ingredient.recipe_id, recipe_ingredient.ingredient_id

## Camadas da Aplicação

### Camada de Apresentação (API Layer)

Responsável por receber requisições HTTP e retornar respostas formatadas.

**Responsabilidades:**
- Definição de rotas e endpoints
- Validação automática de entrada via Pydantic schemas
- Autenticação e autorização
- Documentação automática

**Tecnologias:**
- FastAPI routers
- Pydantic models
- Dependency Injection

### Camada de Serviços (Business Logic Layer)

Contém a lógica de negócio da aplicação, orquestrando operações entre diferentes repositórios.

**Responsabilidades:**
- Implementação de regras de negócio
- Orquestração de operações entre repositórios
- Integração com serviços externos (IA)
- Transformação de dados

**Padrões Utilizados:**
- Service Pattern
- Dependency Injection

### Camada de Repositórios (Data Access Layer)

Abstração do acesso ao banco de dados, encapsulando queries e operações CRUD.

**Responsabilidades:**
- Operações CRUD
- Queries ao banco de dados
- Otimização de consultas (eager loading)

**Padrões Utilizados:**
- Repository Pattern

### Camada de Persistência (Database Layer)

Gerenciamento de conexões e configurações do banco de dados.

**Responsabilidades:**
- Configuração de conexões
- Pool de conexões
- Migrations

## Fluxo de Requisição

1. Cliente envia requisição HTTP para endpoint da API
2. Middleware de autenticação valida JWT token (quando necessário)
3. FastAPI valida automaticamente o payload usando Pydantic schema
4. Router direciona para o handler apropriado
5. Handler injeta dependências (serviços, repositórios)
6. Serviço executa lógica de negócio
7. Repositório realiza operações no banco de dados
8. Dados retornam através das camadas
9. Resposta é serializada automaticamente e enviada ao cliente

## Segurança

### Autenticação

- Autenticação baseada em JWT
- Tokens com informações do usuário
- Verificação de propriedade de recursos

### Configuração

- Variáveis sensíveis em arquivo .env
- Validação automática de entrada via Pydantic
- Proteção contra SQL Injection via ORM

### CORS

- Configuração de origens permitidas para acesso do frontend

## Performance

### Otimizações Básicas

**Banco de Dados:**
- Índices em colunas de busca frequente
- Eager loading de relacionamentos
- Connection pooling via SQLAlchemy

**Aplicação:**
- Paginação de resultados
- Operações assíncronas com FastAPI

## Requisitos

- Python 3.11+
- Conta Supabase (free tier)

## Variáveis de Ambiente

```
SUPABASE_DB_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
```
