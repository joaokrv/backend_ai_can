# 🏋️ AICan — Backend (API REST)

---

## 📌 Sobre o Projeto

O **AICan** é um sistema inteligente de geração automática de **planos de treino personalizados** e **recomendações nutricionais** baseado em integração com modelos de IA. 

O objetivo é oferecer um **protótipo replicável** para pesquisas acadêmicas em personalização de exercícios, validando estratégias de recomendação baseadas em:
- 📊 Dados físicos do usuário (altura, peso, idade, IMC)
- 🎯 Preferências de treino (frequência, local, objetivo)
- 🤖 Inteligência artificial (Google Gemini 2.5 Flash)

---

## 🏗️ Arquitetura e Componentes

O backend foi desenvolvido em **Python** com **FastAPI** seguindo uma arquitetura **modular e escalável**:

| Componente | Descrição |
|-----------|-----------|
| **FastAPI** | Framework Web moderno, validação automática com Pydantic, documentação auto-gerada (Swagger) |
| **SQLAlchemy** | ORM para interação com PostgreSQL, abstração do banco de dados |
| **Alembic** | Versionamento e migração de schema do banco de dados |
| **Google Gemini AI** | Integração com IA para geração inteligente de planos e sugestões |
| **Pydantic** | Validação de dados, serialização JSON e type hints |
| **Python-Jose + Passlib** | Segurança: JWT e hash de senhas |
| **Tenacity** | Retry automático com backoff exponencial para chamadas à API |

---

## 📁 Estrutura do Repositório

```text
backend/
├── main.py                 # Entrada da aplicação, configuração FastAPI
├── requirements.txt        # Dependências Python
├── alembic.ini            # Configuração de migrações
├── .env                   # Variáveis de ambiente (não commitar!)
│
├── app/
│   ├── __init__.py
│   ├── api/               # Camada de API REST
│   │   ├── schemas/       # Modelos Pydantic (requisição/resposta)
│   │   │   ├── exercicio.py
│   │   │   ├── feedback.py
│   │   │   ├── refeicao.py
│   │   │   ├── rotina.py
│   │   │   ├── sugestao.py
│   │   │   └── user.py
│   │   │
│   │   └── v1/            # Versão 1 da API
│   │       ├── routers.py # Registro de rotas
│   │       └── endpoints/ # Endpoints específicos
│   │           └── treino.py
│   │
│   ├── core/              # Configurações centrais
│   │   ├── config.py      # Variáveis de ambiente
│   │   └── security.py    # Autenticação, JWT
│   │
│   ├── database/          # Camada de dados
│   │   ├── base.py        # Configuração SQLAlchemy
│   │   └── models/        # Modelos ORM
│   │       ├── user.py
│   │       ├── exercicio.py
│   │       ├── refeicoes.py
│   │       ├── rotina.py
│   │       └── feedback.py
│   │
│   └── services/          # Lógica de negócio
│       ├── ia_agent.py    # Integração com Google Gemini
│       └── coleta_dados.py
│
└── migrations/            # Histórico de migrações Alembic
    ├── env.py
    ├── script.py.mako
    └── versions/          # Scripts de migração versionados
```

---

## 🔌 Endpoints Disponíveis

### Health Check
```bash
GET /              # Status geral da API
GET /health        # Verificação de saúde
```

### Geração de Planos de Treino
```bash
POST /api/v1/sugestao
```

**Body (JSON):**
```json
{
  "nome": "João",
  "altura": 180,          # cm
  "peso": 80,             # kg
  "idade": 25,
  "disponibilidade": 4,   # dias/semana
  "local": "academia",    # "academia" | "casa" | "arLivre"
  "objetivo": "hipertrofia" # "perder" | "ganhar" | "hipertrofia"
}
```

**Response (JSON):**
```json
{
  "nome_da_rotina": "Treino ABC",
  "dias_de_treino": [
    {
      "foco_muscular": "Peito e Tríceps",
      "identificacao": "Dia 1",
      "exercicios": [
        {
          "nome": "Supino Reto",
          "series": "4",
          "repeticoes": "8-10",
          "descanso_segundos": 120,
          "detalhes_execucao": "Descrição técnica...",
          "video_url": "https://www.youtube.com/results?search_query=supino+reto"
        }
      ]
    }
  ],
  "sugestoes_nutricionais": {
    "pre_treino": {
      "opcao_economica": {
        "nome": "Opção 1",
        "custo_estimado": "R$ 5",
        "ingredientes": ["item1", "item2"],
        "link_receita": "https://www.google.com/search?q=...",
        "explicacao": "..."
      }
    },
    "pos_treino": { }
  }
}
```

---

## 🚀 Configuração e Instalação

### Pré-requisitos
- **Python 3.10+**
- **PostgreSQL 12+**
- **pip** ou **venv**
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
Crie um arquivo `.env` na raiz do projeto:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aican

# Security
SECRET_KEY=sua-chave-secreta-super-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Gemini AI
GEMINI_API_KEY=sua-chave-gemini-aqui

# Debug
DEBUG=True
```

### 5️⃣ Configure o Banco de Dados
```bash
# Aplique migrações Alembic
alembic upgrade head

# Ou crie as tabelas manualmente (requer SQLAlchemy)
python -c "from app.database.base import Base, engine; Base.metadata.create_all(engine)"
```

### 6️⃣ Execute a API
```bash
# Desenvolvimento (com auto-reload)
uvicorn main:app --reload

# Produção
uvicorn main:app --host 0.0.0.0 --port 8000
```

**A API estará disponível em:**
- 🔗 **Aplicação**: http://localhost:8000
- 📚 **Swagger (Docs)**: http://localhost:8000/docs
- 📖 **ReDoc**: http://localhost:8000/redoc

---

---

## 🤖 Integração com Google Gemini

A API utiliza o **Google Gemini 2.5 Flash** para gerar planos de treino inteligentes. O serviço:

- 🔄 **Processa dados do usuário** (altura, peso, idade, objetivo)
- 🧠 **Gera planos personalizados** com exercícios, séries e repetições
- 🍽️ **Recomenda nutrição** com opções economica, equilibrada e premium
- 🔗 **Fornece links** para vídeos no YouTube e receitas no Google
- 🔁 **Implementa retry automático** com backoff exponencial para falhas

**Arquivo principal:** `app/services/ia_agent.py`

**Recurso:** Função `generate_training_plan()` com prompt otimizado

---

## 📤 Deployment

### Opção 1: Render, Railway ou Heroku

1. Configure as variáveis de ambiente na plataforma:
   - `DEBUG=false`
   - `DATABASE_URL` (PostgreSQL)
   - `GEMINI_API_KEY`
   - `SECRET_KEY`

1. Defina o comando de inicialização:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

1. Adicione PostgreSQL (extensão na plataforma)
1. Faça deploy da branch `main` ou `develop/backend.joao_carvalho`

> ⚠️ Nota para Render: certifique-se de usar **Build Command** como `pip install -r requirements.txt` e **Start Command** como:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. Adicione PostgreSQL (extensão na plataforma)
4. Faça deploy da branch `main` ou `develop/backend.joao_carvalho`

### Opção 2: Docker

Crie um `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Construa e execute:

```bash
docker build -t aican-backend .
docker run -p 8000:8000 --env-file .env aican-backend
```

### Opção 3: Bare Metal / VPS

```bash
# 1. SSH na máquina
ssh user@seu-servidor.com

# 2. Clone o repositório
git clone https://github.com/joaokrv/backend_ai_can.git
cd backend

# 3. Configure ambiente
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure .env com suas credenciais

# 5. Inicie com supervisord, systemd ou PM2
# Exemplo com PM2:
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name aican-api
```

---

## 🧪 Testes

Para adicionar testes unitários:

```bash
# Instale pytest
pip install pytest pytest-asyncio

# Crie testes em tests/ (exemplo)
pytest tests/ -v
```

---

## 📊 Estrutura de Dados

### User

- `id` (UUID)
- `nome` (str)
- `email` (str, único)
- `altura` (float, cm)
- `peso` (float, kg)
- `idade` (int)
- `criado_em` (datetime)

### Rotina

- `id` (UUID)
- `user_id` (FK)
- `nome` (str)
- `descricao` (text)
- `dias_treino` (int)
- `criada_em` (datetime)

### Exercício

- `id` (UUID)
- `rotina_id` (FK)
- `nome` (str)
- `séries` (int)
- `repetições` (str)
- `descanso` (int, segundos)

---

## ❓ Troubleshooting

### Erro: `DATABASE_URL not configured`

- Verifique se `.env` existe e contém `DATABASE_URL`
- Certifique-se de que PostgreSQL está rodando
- Teste a conexão: `psql <DATABASE_URL>`

### Erro: `GEMINI_API_KEY not found`

- Obtenha a chave em [Google AI Studio](https://aistudio.google.com)
- Adicione ao arquivo `.env`
- Reinicie a aplicação

### Erro: `Connection refused on port 8000`

- Verifique se a API não está rodando em outro processo
- Tente outra porta: `uvicorn main:app --port 8001`
- Verifique se não há firewall bloqueando

### Erro: `CORS error`

- Verifique `main.py` - configure `allow_origins` corretamente
- Adicione a URL do frontend: `allow_origins=["http://seu-frontend.com"]`

---

## 📚 Recursos e Documentação

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Google Gemini API](https://ai.google.dev/)
- [Pydantic Validation](https://docs.pydantic.dev/)

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
- Documente funções
- Escreva testes quando possível

---

## 📄 Licença

Trabalho acadêmico para fins educacionais.

---

## 👥 Autores

- **João Victor Carvalho** - [GitHub](https://github.com/joaokrv)

---

## 🔄 Melhorias Futuras

- [ ] Autenticação JWT completa
- [ ] Histórico de planos por usuário
- [ ] Cache de respostas da IA (Redis)
- [ ] Rate limiting por usuário
- [ ] Sistema de avaliação de planos
- [ ] Integração com Stripe para planos premium
- [ ] Notificações por email
- [ ] Dashboard analytics
- [ ] Suporte a múltiplos idiomas

---

## 📞 Suporte

Para dúvidas ou problemas, abra uma **issue** no repositório.
