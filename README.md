# 🏋️ AICan - Backend API

API REST para geração de planos de treino personalizados usando Inteligência Artificial (Cerebras AI).

## 📋 Sobre o Projeto

O **AICan** é uma aplicação web que permite aos usuários gerarem planos de treino e dieta personalizados baseados em seus dados físicos e objetivos. A IA analisa as informações fornecidas (altura, peso, idade, disponibilidade, local de treino e objetivo) e retorna um plano completo e detalhado.

### ✨ Funcionalidades

- 🤖 Geração de planos de treino personalizados com IA
- 📊 Análise de perfil físico (IMC, idade, objetivos)
- 🏋️ Exercícios detalhados com séries, repetições e tempo de descanso
- 🥗 Sugestões nutricionais pré e pós-treino (econômica, equilibrada, premium)
- 🔗 Links para vídeos de demonstração dos exercícios
- 📖 Documentação automática com Swagger UI

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **Python 3.10+** - Linguagem de programação
- **Cerebras AI** - API de Inteligência Artificial
- **PostgreSQL** - Banco de dados relacional
- **SQLAlchemy** - ORM para Python
- **Alembic** - Migrações de banco de dados
- **Pydantic** - Validação de dados
- **Tenacity** - Retry automático para APIs

## 📁 Estrutura do Projeto

```
backend/
├── app/
│   ├── api/
│   │   ├── schemas/          # Validação de entrada/saída
│   │   │   ├── sugestao.py   # Schema de sugestão
│   │   │   ├── user.py
│   │   │   └── ...
│   │   └── v1/
│   │       ├── routers.py    # Agregador de rotas
│   │       └── endpoints/    # Endpoints da API
│   │           └── treino.py
│   ├── core/
│   │   ├── config.py         # Configurações e variáveis de ambiente
│   │   └── security.py       # Autenticação e segurança
│   ├── database/
│   │   ├── base.py           # Conexão com banco
│   │   └── models/           # Modelos SQLAlchemy
│   └── services/
│       └── ia_agent.py       # Integração com Cerebras AI
├── migrations/               # Migrações do Alembic
├── main.py                   # Ponto de entrada da aplicação
├── requirements.txt          # Dependências
└── README.md
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- PostgreSQL 13+
- Conta na [Cerebras AI](https://cloud.cerebras.ai/)
- Git

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/backend_ai_can.git
cd backend_ai_can
```

### 2. Crie um Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente

Crie um arquivo `.env` na raiz do backend com suas credenciais.

**⚠️ IMPORTANTE:** O arquivo `.env` nunca deve ser commitado no Git!

### 5. Execute as Migrações do Banco (Opcional)

```bash
# Modo desenvolvimento (com auto-reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Modo produção
uvicorn main:app --host 0.0.0.0 --port 8000
```

O servidor estará disponível em: `http://localhost:8000`

### Principais Endpoints

#### `POST /api/v1/sugestao/sugestao`

Gera um plano de treino personalizado.

**Request Body:**
```json
{
  "nome": "João Silva",
  "altura": 175,
  "peso": 80,
  "idade": 30,
  "disponibilidade": 3,
  "local": "academia",
  "objetivo": "hipertrofia"
}
```

**Response:** Plano de treino completo com exercícios e sugestões nutricionais.

#### `GET /health`

Verifica se a API está funcionando.

**Response:**
```json
{
  "status": "healthy"
}
```

## 🔒 Segurança

### Boas Práticas Implementadas

✅ **Variáveis de ambiente** para credenciais sensíveis  
✅ **Validação de entrada** com Pydantic  
✅ **CORS configurado** para permitir apenas origens específicas  
✅ **Logging estruturado** para auditoria  
✅ **Retry automático** com backoff exponencial  
✅ **Tratamento de erros** robusto  
✅ **Type hints** em todo o código

### ⚠️ Checklist de Segurança

Antes de fazer deploy em produção:

- [ ] Arquivo `.env` está no `.gitignore`
- [ ] Credenciais não estão hardcoded no código
- [ ] `DEBUG=False` em produção
- [ ] CORS configurado apenas para domínios confiáveis
- [ ] HTTPS habilitado
- [ ] Variáveis de ambiente configuradas no servidor

## 🧪 Testes

```bash
# Executar testes (quando implementado)
pytest

# Com coverage
pytest --cov=app tests/
```

## 📦 Deploy

### Render / Heroku / Railway

1. Configure as variáveis de ambiente no painel da plataforma
2. Defina o comando de start:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Configure o banco PostgreSQL
4. Faça deploy da branch `main`

### Docker (Opcional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t aican-backend .
docker run -p 8000:8000 --env-file .env aican-backend
```

## 🐛 Troubleshooting

### Erro: "CEREBRAS_API_KEY não configurada"

**Solução:** Verifique se o arquivo `.env` existe e contém a chave `CEREBRAS_API_KEY`.

### Erro: "Connection refused" ao banco

**Solução:** Verifique se o PostgreSQL está rodando e se a `DATABASE_URL` está correta.

### Erro: "Module not found"

**Solução:** Certifique-se de que o ambiente virtual está ativado e as dependências instaladas:
```bash
pip install -r requirements.txt
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é um trabalho acadêmico desenvolvido para fins educacionais.

## 👥 Autores

- **Seu Nome** - [GitHub](https://github.com/joaokrv)

## 📞 Suporte

Para dúvidas ou problemas, abra uma [issue](https://github.com/joaokrv/backend_ai_can/issues) no GitHub.

---

**Desenvolvido com ❤️ usando FastAPI e Cerebras AI**
