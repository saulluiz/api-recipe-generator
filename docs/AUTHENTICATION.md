 # Sistema de Autenticação

## Visão Geral

O sistema de autenticação da API Recipe Generator utiliza JWT (JSON Web Tokens) para autenticar usuários de forma stateless. O processo é simples e direto, adequado para um projeto acadêmico.

## Fluxo de Autenticação

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       │ 1. POST /auth/register
       │    { username, email, password, full_name }
       ▼
┌─────────────────┐
│      API        │ ──► Salva usuário no banco (senha em texto)
└─────────────────┘
       │
       │ 2. POST /auth/login
       │    { username, password }
       ▼
┌─────────────────┐
│      API        │ ──► Verifica credenciais
└─────────────────┘ ──► Gera JWT token
       │
       │ 3. Retorna token
       │    { "access_token": "eyJ...", "token_type": "bearer" }
       ▼
┌─────────────┐
│   Cliente   │ ──► Armazena token
└──────┬──────┘
       │
       │ 4. GET /recipes
       │    Header: Authorization: Bearer eyJ...
       ▼
┌─────────────────┐
│      API        │ ──► Valida token
└─────────────────┘ ──► Extrai dados do usuário
       │              ──► Processa requisição
       ▼
   Resposta
```

## Endpoints de Autenticação

### 1. Registro de Usuário

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "username": "joao",
  "email": "joao@email.com",
  "password": "senha123",
  "full_name": "João Silva"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-aqui",
  "username": "joao",
  "email": "joao@email.com",
  "full_name": "João Silva"
}
```

**Validações:**
- Username único
- Email único e válido
- Password obrigatório
- Full name obrigatório

### 2. Login

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "joao",
  "password": "senha123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Erros:**
- 401 Unauthorized: Credenciais inválidas

### 3. Obter Usuário Atual

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "id": "uuid-aqui",
  "username": "joao",
  "email": "joao@email.com",
  "full_name": "João Silva"
}
```

## Estrutura do JWT Token

### Payload do Token

```json
{
  "sub": "user-uuid",
  "username": "joao",
  "email": "joao@email.com",
  "exp": 1234567890
}
```

**Campos:**
- `sub` (subject): ID do usuário
- `username`: Nome de usuário
- `email`: Email do usuário
- `exp` (expiration): Timestamp de expiração

### Configurações do Token

- **Algoritmo:** HS256 (HMAC with SHA-256)
- **Secret Key:** Definida em `.env` (SECRET_KEY)
- **Expiração:** Configurável (padrão não definido ainda)

## Middleware de Autenticação

### Função: `get_current_user`

Dependency do FastAPI que:
1. Extrai o token do header `Authorization`
2. Valida o token
3. Decodifica o payload
4. Busca o usuário no banco de dados
5. Retorna o usuário autenticado

### Uso em Rotas Protegidas

```python
@router.get("/recipes/my-recipes")
async def get_my_recipes(current_user: User = Depends(get_current_user)):
    # current_user contém os dados do usuário autenticado
    return recipes_by_user(current_user.id)
```

## Rotas Públicas vs Protegidas

### Rotas Públicas (sem autenticação)
- `POST /auth/register` - Criar conta
- `POST /auth/login` - Fazer login
- `GET /recipes` - Listar todas as receitas
- `GET /recipes/{id}` - Ver detalhes de uma receita
- `GET /ingredients` - Listar ingredientes

### Rotas Protegidas (requerem token)
- `GET /auth/me` - Dados do usuário atual
- `POST /recipes` - Criar receita
- `PUT /recipes/{id}` - Editar receita (apenas do próprio usuário)
- `DELETE /recipes/{id}` - Deletar receita (apenas do próprio usuário)
- `POST /recipes/generate` - Gerar receita com IA

## Verificação de Propriedade

Para operações de edição e exclusão, além de verificar se o usuário está autenticado, verificamos se ele é o dono do recurso:

```python
# Exemplo de verificação
if recipe.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Não autorizado")
```

## Implementação

### Arquivos Envolvidos

1. **`src/core/security.py`**
   - Criação de tokens JWT
   - Verificação de tokens JWT
   - Função para obter usuário atual

2. **`src/api/middlewares/auth.py`**
   - Dependency `get_current_user`
   - Extração do token do header

3. **`src/api/routes/users.py`**
   - Endpoints de registro e login
   - Endpoint para obter dados do usuário atual

4. **`src/services/user_service.py`**
   - Lógica de criação de usuário
   - Validação de credenciais de login

5. **`src/repositories/user_repository.py`**
   - Busca de usuário por username
   - Busca de usuário por email
   - Busca de usuário por ID
   - Criação de novo usuário

## Fluxo de Dados

### Registro
```
Cliente → Router (users.py) → Service (user_service.py) → Repository (user_repository.py) → Database
                                                                                              ↓
Cliente ← Router ← Service ← Repository ←─────────────────────────────────────────────────────┘
```

### Login
```
Cliente → Router (users.py) → Service (user_service.py) → Repository (busca usuário) → Database
                                     ↓
                              Valida password
                                     ↓
                              Security (cria token JWT)
                                     ↓
Cliente ←────────────────────────────┘
```

### Requisição Autenticada
```
Cliente → Middleware (auth.py) → Security (valida token) → Repository (busca usuário) → Database
              ↓                                                                             ↓
         Extrai token                                                                       ↓
              ↓                                                                             ↓
         Router (com user) ←──────────────────────────────────────────────────────────────┘
```

## Tratamento de Erros

### Erros de Autenticação

- **401 Unauthorized**
  - Token inválido
  - Token expirado
  - Token não fornecido
  - Credenciais inválidas no login

- **403 Forbidden**
  - Usuário não tem permissão para acessar/modificar o recurso

- **409 Conflict**
  - Username já existe
  - Email já existe

## Segurança

### Considerações

1. **Senha em texto plano**: Para simplificar o projeto acadêmico, as senhas são armazenadas sem hash
2. **Token sem refresh**: Sistema simplificado sem refresh tokens
3. **Validação básica**: Validações mínimas necessárias

### Headers HTTP

**Requisição com autenticação:**
```
GET /recipes/my-recipes HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Exemplo de Uso

### 1. Registrar novo usuário
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria",
    "email": "maria@email.com",
    "password": "senha456",
    "full_name": "Maria Santos"
  }'
```

### 2. Fazer login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria",
    "password": "senha456"
  }'
```

### 3. Usar o token em requisições
```bash
curl -X GET http://localhost:8000/recipes/my-recipes \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## Configuração

### Variáveis de Ambiente

```env
SECRET_KEY=sua-chave-secreta-super-segura-aqui
```

A SECRET_KEY é usada para assinar os tokens JWT. Deve ser uma string aleatória e mantida em segredo.
