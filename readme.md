<h1 align="center">🛡️ Sparta Gym | Backend API</h1>
<p align="center">
<b>Clone o projeto:</b>
</p>

```bash
git clone https://github.com/DanielPupo/api-backend-catraca.git
```


<p align="center">
API REST para gerenciamento de alunos e controle de acesso via catraca do sistema Sparta Gym.
</p>

---

## 📌 Sobre o Projeto

O Sparta Gym é um sistema completo de gerenciamento para academias, permitindo:

- Controle de entrada via catraca usando CPF
- Gerenciamento administrativo de alunos
- Integração com frontend moderno (Admin Panel)
- Persistência de dados em nuvem (Firebase)

---

## 🚀 Funcionalidades

- 🔐 Autenticação de administrador com JWT
- 👥 CRUD completo de alunos
- 🚪 Validação de acesso na catraca
- ☁️ Integração com Firebase Firestore
- 🧾 Geração automática de IDs sequenciais
- 🛡️ Proteção de rotas com middleware
- 📄 Documentação com Swagger (OpenAPI 3.0)
- 🌐 Suporte a CORS

---

## 🧠 Tecnologias Utilizadas

- Python
- Flask
- Firebase Admin SDK
- Firestore (NoSQL)
- JWT (JSON Web Token)
- Flask-CORS
- Python-dotenv
- Flasgger (Swagger)

---

## ⚙️ Arquitetura da API

A API segue o padrão REST, com separação clara entre:

- 🔓 **Rotas públicas**: acesso livre (catraca)
  
- 🔒 **Rotas privadas**: requer autenticação JWT
- ⚠️ Tratamento global de erros

---

## 🔑 Autenticação

### Endpoint de Login

```http
POST /login
```

**Body:**
```json
{
  "usuario": "admin",
  "senha": "sua_senha"
}
```

**Fluxo:**
1. Usuário envia credenciais
2. API valida com variáveis `.env`
3. Token JWT é gerado (`gerar_token`)
4. Token deve ser enviado nas rotas protegidas

**Header obrigatório:**
```
Authorization: Bearer SEU_TOKEN
```

---

## 🚪 Rota Pública (Catraca)

Verifica acesso do aluno:

```http
POST /catraca
```

**Body:**
```json
{
  "cpf": "12345678900"
}
```

**Lógica aplicada:**
- Busca aluno pelo CPF no Firestore
- Se não encontrado → 404
- Se `status == false` → BLOQUEADO
- Caso contrário → LIBERADO

**Respostas:**
```json
{
  "status": "LIBERADO",
  "nome": "João"
}
```
```json
{
  "status": "BLOQUEADO"
}
```

---

## 🔒 Rotas Privadas (Alunos)

Todas utilizam o decorator:
```python
@token_obrigatorio
```

### 📋 Listar alunos
```http
GET /alunos
```
Retorna todos os alunos com `doc_id`.

### ➕ Criar aluno
```http
POST /alunos
```
**Validações:**
- CPF obrigatório
- Nome obrigatório
- CPF deve conter 11 dígitos
- CPF deve ser único

**Regras internas:**
- Remove caracteres não numéricos do CPF
- Gera ID sequencial via coleção contador

### ✏️ Editar aluno
```http
PUT /alunos/{id}
```
**Validações:**
- CPF com 11 dígitos
- CPF não pode duplicar (exceto o próprio registro)

### ❌ Excluir aluno
```http
DELETE /alunos/{id}
```
Remove o aluno do Firestore.

---

## 🧠 Regras de Negócio

- CPF é armazenado apenas com números
- CPF deve ser único no sistema
- `status` define acesso:
  - `true` → LIBERADO
  - `false` → BLOQUEADO
- IDs são gerados incrementalmente (contador manual)

---

## ☁️ Integração com Firebase

### Modos de execução

- **Local:**
  - Arquivo: `firebase.json`
- **Produção (Vercel):**
  - Variável de ambiente: `FIREBASE_CREDENTIALS={JSON_DO_FIREBASE}`

---

## ⚙️ Variáveis de Ambiente

Arquivo `.env`:
```env
SECRET_KEY=sua_chave_secreta
ADM_USUARIO=admin
ADM_SENHA=sua_senha
```

---

## ▶️ Execução do Backend

```bash
pip install flask firebase-admin flask-cors python-dotenv flasgger
python app.py
```

API disponível em: [http://localhost:5000](http://localhost:5000)

---

## 📄 Documentação Swagger

Disponível em: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)
Utiliza arquivo externo: `openapi.yaml`

Utiliza arquivo externo:

openapi.yaml
⚠️ Tratamento de Erros

A API possui handlers globais:

400 → Dados inválidos
401 → Não autorizado
404 → Não encontrado
409 → Conflito (CPF duplicado)
---

## ⚠️ Tratamento de Erros

A API possui handlers globais para:

- `400` → Dados inválidos
- `401` → Não autorizado
- `404` → Não encontrado
- `409` → Conflito (CPF duplicado)
- `500` → Erro interno

---

## 🔐 Segurança

- Uso de JWT para autenticação
- Rotas protegidas com decorator
- CPF validado e sanitizado
- Variáveis sensíveis via `.env`

**Melhorias futuras:**
- Expiração e refresh token
- Rate limiting
- Logs de auditoria
- Criptografia adicional

---

## ⚠️ Observações Técnicas

- Firestore usado como banco NoSQL
- Sistema de ID manual pode ser substituído futuramente
- Token JWT depende do `SECRET_KEY`
- API preparada para deploy em serverless (Vercel)

---

## 👥 Desenvolvedores

- **Daniel Pupo** https://github.com/DanielPupo
- **João Guilherme** https://github.com/jgarrudaa

---

## 🌍 Deploy

- 🔗 Frontend Admin: [https://administrativo-academia.vercel.app/](https://administrativo-academia.vercel.app/)
- 🔗 Frontend Catraca: [https://catraca-academia-six.vercel.app/](https://catraca-academia-six.vercel.app/)
- 🔗 Backend: [https://api-backend-catraca.vercel.app](https://api-backend-catraca.vercel.app)

---

## 💡 Sobre o Backend

Este backend foi projetado para simular um ambiente real de academia, incluindo:

- Controle de acesso físico (catraca)
- Validação em tempo real via API
- Persistência segura em nuvem
- Integração com painel administrativo