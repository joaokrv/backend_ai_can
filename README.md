# 🏋️ AICan — Backend (API REST)

---

## 📌 Sobre o Projeto

O **AICan** é um sistema inteligente de geração automática de **planos de treino personalizados** e **recomendações nutricionais** baseado em integração com modelos de IA. 

O objetivo é oferecer um **protótipo replicável** para pesquisas acadêmicas em personalização de exercícios, validando estratégias de recomendação baseadas em:
- 📊 Dados físicos do usuário (altura, peso, idade, IMC)
- 🎯 Preferências de treino (frequência, local, objetivo)
- 🤖 Inteligência artificial (Google Gemini 2.0 Flash)
- 👍👎 Feedback adaptativo do usuário (sistema de aprendizado)

---

## 🏗️ Arquitetura e Componentes

O backend foi desenvolvido em **Python** com **FastAPI** seguindo uma arquitetura **modular e escalável**:

| Componente | Descrição |
|-----------|-----------| 
| **FastAPI 0.115** | Framework Web moderno, validação automática com Pydantic, documentação auto-gerada |
| **SQLAlchemy 2.0** | ORM para interação com PostgreSQL, abstração do banco de dados |
| **Alembic 1.14** | Versionamento e migração de schema do banco de dados |
| **Google Gemini AI** | Integração com google-genai 1.51 para geração inteligente de planos |
| **Pydantic 2.9** | Validação de dados, serialização JSON e type hints |
| **Python-Jose + Passlib** | Segurança: JWT e hash de senhas (bcrypt) |
| **Tenacity 9.0** | Retry automático com backoff exponencial |
| **SlowAPI 0.1.9** | Rate limiting para proteção de endpoints |

---

## 📁 Estrutura do Projeto

```
backend/
├── main.py                    # Ponto de entrada da aplicação
├── requirements.txt           # Dependências Python
├── alembic.ini               # Configuração do Alembic
├── .env                      # Variáveis de ambiente
├── API_FLOWS.md              # Documentação de fluxos da API
│
├── app/
│   ├── __init__.py
│   │
│   ├── api/
│   │   ├── deps.py           # Dependências de injeção (DB, Auth)
│   │   │
│   │   ├── schemas/          # Schemas Pydantic
│   │   │   ├── user.py       # UserCreate, UserResponse, Token
│   │   │   ├── sugestao.py   # SugestaoCreate
│   │   │   ├── plano.py      # PlanoIAResponse
│   │   │   ├── feedback.py   # FeedbackCreate, FeedbackResponse, Stats
│   │   │   ├── exercicio.py  # Schemas de exercício
│   │   │   └── refeicao.py   # Schemas de refeição
│   │   │
│   │   └── v1/
│   │       ├── routers.py    # Configuração de rotas
│   │       └── endpoints/
│   │           ├── auth.py   # Login, registro, /me
│   │           ├── treino.py # Geração de planos com IA
│   │           └── feedback.py # Sistema de feedback adaptativo
│   │
│   ├── core/
│   │   ├── config.py         # Settings (Pydantic BaseSettings)
│   │   └── security.py       # JWT, hash de senhas
│   │
│   ├── database/
│   │   ├── base.py           # Configuração SQLAlchemy
│   │   └── models/
│   │       ├── user.py       # Modelo User
│   │       ├── plano.py      # Plano, PlanoDia, PlanoExercicio
│   │       ├── nutricao.py   # PlanoRefeicao
│   │       ├── feedback.py   # Feedback (preferências)
│   │       └── catalogo_exercicio.py # Catálogo de exercícios
│   │
│   └── services/
│       ├── ia_agent.py       # Integração Google Gemini
│       └── coleta_dados.py   # Processamento de dados
│
└── migrations/
    ├── env.py
    ├── script.py.mako
    └── versions/             # Migrações Alembic
```

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- **Python 3.10+** (recomendado: 3.11 ou 3.12)
- **PostgreSQL 12+**
- **pip** e **venv**
- **Chave API do Google Gemini** (obter em [Google AI Studio](https://aistudio.google.com))

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/joaokrv/backend_ai_can.git
cd backend
```

### 2️⃣ Crie um Ambiente Virtual

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
# Database
DATABASE_URL=postgresql://usuario:senha@localhost:5432/aican_db

# Security
SECRET_KEY=sua-chave-secreta-super-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Gemini AI
GEMINI_API_KEY=sua-api-key-do-gemini

# Environment
DEBUG=false
```

### 5️⃣ Configure o Banco de Dados

```bash
# Aplique migrações Alembic
alembic upgrade head
```

### 6️⃣ Execute a API

```bash
# Desenvolvimento (com auto-reload)
uvicorn main:app --reload

# Produção
uvicorn main:app --host 0.0.0.0 --port 8000
```

**A API estará disponível em:**

- 🔗 **Aplicação**: <http://localhost:8000>
- 📚 **Swagger (Docs)**: <http://localhost:8000/docs>
- 📖 **ReDoc**: <http://localhost:8000/redoc>

---

## 🤖 Integração com Google Gemini

A API utiliza o **Google Gemini 2.0 Flash** via biblioteca `google-genai` para gerar planos de treino inteligentes. O serviço:

- 🔄 **Processa dados do usuário** (altura, peso, idade, objetivo)
- 🧠 **Gera planos personalizados** com exercícios, séries e repetições
- 🍽️ **Recomenda nutrição** com opções econômica, equilibrada e premium
- 🔗 **Fornece links** para vídeos no YouTube e receitas no Google
- 🔁 **Implementa retry automático** com backoff exponencial (Tenacity)
- 🎯 **Aplica preferências** do usuário (evita itens rejeitados)

**Arquivo principal:** `app/services/ia_agent.py`

**Função principal:** `generate_training_plan()` com prompt otimizado

### Sistema de Feedback Adaptativo

A API inclui um **sistema de feedback** que personaliza futuros planos baseado nas preferências do usuário:

- 👍👎 **Avaliação de itens**: Usuários podem marcar exercícios/refeições como "gostei" ou "não gostei"
- 🔄 **Adaptação automática**: Planos futuros evitam automaticamente itens rejeitados via `obter_preferencias_usuario()`
- 📊 **Estatísticas**: Taxa de satisfação, itens mais rejeitados, totais de feedback
- 🎯 **Agente inteligente**: Demonstra personalização baseada em dados e aprendizado iterativo

**Documentação completa:**
- [Fluxos da API](./API_FLOWS.md) - Detalhes de autenticação, geração de planos, persistência e sistema de feedback.

---

## 📡 Endpoints da API

### Autenticação (`/api/v1/auth`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/register` | Criar conta (rate limit: 3/hora) | ❌ |
| `POST` | `/login` | Login (retorna JWT token) | ❌ |
| `GET` | `/me` | Dados do usuário autenticado | ✅ |

### Geração de Planos (`/api/v1/sugestao`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/` | Gerar plano de treino personalizado com IA | ✅ |

**Request Body:**
```json
{
  "nome": "João Silva",
  "altura": 175,
  "peso": 80,
  "idade": 25,
  "disponibilidade": 4,
  "local": "academia",
  "objetivo": "hipertrofia"
}
```

**Response:** Plano completo com exercícios por dia e sugestões nutricionais (pré e pós-treino).

### Feedback (`/api/v1/feedback`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| `POST` | `/exercicio` | Avaliar exercício (gostei/não gostei) | ✅ |
| `POST` | `/refeicao` | Avaliar refeição (gostei/não gostei) | ✅ |
| `GET` | `/me` | Listar preferências do usuário | ✅ |
| `GET` | `/stats` | Estatísticas de feedback | ✅ |
| `DELETE` | `/{feedback_id}` | Deletar feedback específico | ✅ |

**Feedback Request:**
```json
{
  "item_nome": "Supino reto",
  "gostou": false,
  "comentario": "Causa dor no ombro"
}
```

**Stats Response:**
```json
{
  "total_feedbacks": 15,
  "total_positivos": 12,
  "total_negativos": 3,
  "taxa_satisfacao": 80.0,
  "exercicios_mais_rejeitados": ["Supino reto", "Leg press"],
  "refeicoes_mais_rejeitadas": ["Ovo cozido"]
}
```

---

## 🔐 Segurança

| Recurso | Implementação |
|---------|---------------|
| **Autenticação** | JWT (python-jose) com expiração configurável |
| **Hash de Senhas** | bcrypt via Passlib |
| **Rate Limiting** | SlowAPI (3 cadastros/hora por IP) |
| **Validação** | Pydantic v2 com type hints |
| **CORS** | Configurável por ambiente |
| **Environment** | Variáveis sensíveis em `.env` |

---

## 🗄️ Modelos do Banco de Dados

### User
- `id`, `email`, `hash_senha`, `nome`
- `idade`, `altura`, `peso`
- `local_treino`, `frequencia_semana`, `objetivo`
- `is_active`, `created_at`

### Plano
- `id`, `nome`, `descricao`, `usuario_id`
- **PlanoDia**: `identificacao`, `foco_muscular`, `ordem`
- **PlanoExercicio**: `nome`, `series`, `repeticoes`, `descanso_segundos`, `video_url`

### PlanoRefeicao
- `plano_id`, `nome`, `tipo` (pre/pos)
- `nivel` (economica/equilibrada/premium)
- `custo_estimado`, `ingredientes`, `link_receita`

### Feedback
- `usuario_id`, `tipo` (exercicio/refeicao)
- `item_nome`, `gostou`, `comentario`
- `created_at`

---

## 📦 Dependências Principais

```txt
# Core
fastapi==0.115.0
uvicorn==0.32.0
pydantic==2.9.2
pydantic-settings==2.6.0

# Database
sqlalchemy==2.0.36
psycopg2-binary==2.9.10
alembic==1.14.0

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.20

# AI Integration
google-genai==1.51.0

# Resilience
tenacity==9.0.0
httpx==0.28.1
slowapi==0.1.9
```

---

## 📚 Recursos e Documentação

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 ORM](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Google Gemini API (genai)](https://ai.google.dev/gemini-api/docs)
- [Pydantic v2 Validation](https://docs.pydantic.dev/)
- [Tenacity Retry](https://tenacity.readthedocs.io/)

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/MinhaFeature`
3. Faça commits descritivos: `git commit -m 'Adiciona MinhaFeature'`
4. Push para a branch: `git push origin feature/MinhaFeature`
5. Abra um Pull Request com descrição clara

**Guia de código:**

- Siga PEP 8
- Use type hints
- Documente funções complexas com docstrings
- Evite comentários óbvios
- Prefira async/await para endpoints

---

## 📄 Licença

Trabalho acadêmico para fins educacionais.

---

## 👥 Autores

- **João Victor Carvalho** - [GitHub](https://github.com/joaokrv)

---

## 📞 Suporte

Para dúvidas ou problemas, abra uma **issue** no repositório.

---

**Última atualização:** 27 de novembro de 2025  
**Versão:** 2.1.0  
**Status:** ✅ Ativo
