# 🏋️ AICan — Backend (API REST)

---

## 📌 Sobre o Projeto

O **AICan** é um sistema inteligente de geração automática de **planos de treino personalizados** e **recomendações nutricionais** baseado em integração com modelos de IA. 

O objetivo é oferecer um **protótipo replicável** para pesquisas acadêmicas em personalização de exercícios, validando estratégias de recomendação baseadas em:
- 📊 Dados físicos do usuário (altura, peso, idade, IMC)
- 🎯 Preferências de treino (frequência, local, objetivo)
- 🤖 Inteligência artificial (Google Gemini 2.0 Flash)
- 👍👎 Feedback do usuário (sistema adaptativo)

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

A API utiliza o **Google Gemini 2.0 Flash** para gerar planos de treino inteligentes. O serviço:

- 🔄 **Processa dados do usuário** (altura, peso, idade, objetivo)
- 🧠 **Gera planos personalizados** com exercícios, séries e repetições
- 🍽️ **Recomenda nutrição** com opções econômica, equilibrada e premium
- 🔗 **Fornece links** para vídeos no YouTube e receitas no Google
- 🔁 **Implementa retry automático** com backoff exponencial para falhas

**Arquivo principal:** `app/services/ia_agent.py`

**Recurso:** Função `generate_training_plan()` com prompt otimizado

### Sistema de Feedback Adaptativo

A API inclui um **sistema de feedback** que personaliza futuros planos baseado nas preferências do usuário:

- 👍👎 **Avaliação de itens**: Usuários podem marcar exercícios/refeições como "gostei" ou "não gostei"
- 🔄 **Adaptação automática**: Planos futuros evitam automaticamente itens rejeitados
- 📊 **Estatísticas**: Taxa de satisfação e itens mais rejeitados
- 🎯 **Agente inteligente**: Demonstra personalização baseada em dados e aprendizado iterativo

**Documentação completa:**
- [Fluxos da API](./API_FLOWS.md) - Detalhes de autenticação, geração de planos, persistência e sistema de feedback.

---

## 📡 Principais Endpoints

### Autenticação
- `POST /api/v1/auth/register` - Criar conta
- `POST /api/v1/auth/login` - Login (retorna JWT token)
- `GET /api/v1/auth/me` - Dados do usuário autenticado

### Geração de Planos
- `POST /api/v1/sugestao` - Gerar plano de treino personalizado com IA

### Feedback
- `POST /api/v1/feedback/ejercicio` - Avaliar exercício
- `POST /api/v1/feedback/refeicao` - Avaliar refeição
- `GET /api/v1/feedback/me` - Listar preferências
- `GET /api/v1/feedback/stats` - Estatísticas
- `DELETE /api/v1/feedback/{id}` - Deletar feedback

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
- Documente funções complexas
- Evite comentários óbvios

---

## 📄 Licença

Trabalho acadêmico para fins educacionais.

---

## 👥 Autores

- **João Victor Carvalho** - [GitHub](https://github.com/joaokrv)

---

## 📞 Suporte

Para dúvidas ou problemas, abra uma **issue** no repositório.
