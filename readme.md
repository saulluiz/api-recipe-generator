# Repositorios
https://github.com/saulluiz/api-recipe-generator (atual)
https://github.com/italo71/recipe-generator (front-end)

## API Recipe Generator

## Descrição do Projeto

API Recipe Generator é um sistema backend desenvolvido para gerenciar e gerar receitas culinárias de forma inteligente. A aplicação oferece funcionalidades completas de CRUD para receitas, ingredientes e usuários, além de integração com inteligência artificial para geração automatizada de receitas baseadas em ingredientes disponíveis.

### Principais Funcionalidades

- Gerenciamento completo de receitas (criar, ler, atualizar, deletar)
- Cadastro e gerenciamento de ingredientes
- Sistema de autenticação de usuários com JWT
- Geração automática de receitas através de IA (OpenAI/Gemini)
- Relacionamento entre receitas e ingredientes
- Documentação interativa da API via Swagger UI

### Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **Supabase** - Banco de dados PostgreSQL gerenciado
- **Pydantic** - Validação de dados
- **OpenAI API** - Integração com inteligência artificial
- **LangChain** - Orquestração de LLMs
- **JWT** - Autenticação baseada em tokens

## Pré-requisitos

Antes de começar, você precisa ter instalado em sua máquina:

- **Python 3.11+** - [Download aqui](https://www.python.org/downloads/)
- **pip** - Gerenciador de pacotes Python (geralmente vem com Python)
- **Git** - [Download aqui](https://git-scm.com/downloads)
- **Conta Supabase** - [Criar conta gratuita](https://supabase.com)
- **Chave API OpenAI** - [Criar conta e obter API key](https://platform.openai.com)

## Como Rodar

### 1. Crie e ative o ambiente virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Inicie o servidor

```bash
uvicorn src.meu_app.main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

### Acessar a Documentação

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Desativar o ambiente virtual

Quando terminar de trabalhar:

```bash
deactivate
```

## Estrutura do Projeto

```
src/
├── api/
│   ├── routes/          # Endpoints da API
│   ├── middlewares/     # Middlewares (autenticação, etc)
│   └── schemas/         # Schemas Pydantic
├── core/                # Configurações centrais
├── models/              # Modelos SQLAlchemy
├── services/            # Lógica de negócio
├── repositories/        # Acesso ao banco de dados
└── database/            # Configuração do banco
```

## Documentação

Para mais detalhes sobre a arquitetura do projeto, consulte:
- [Documentação da Arquitetura](docs/ARCHITECTURE.md)
