from logging.config import fileConfig
import sys
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Importa Base e carrega todos os modelos
from app.database.base import Base
from app.database.models import user, plano, catalogo_exercicio, nutricao, feedback
from app.core.config import settings

# Este é o objeto de configuração do Alembic, que fornece
# acesso aos valores definidos no arquivo .ini em uso.
config = context.config

# Sobrescreve a URL do banco com a do .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpreta o arquivo de configuração para logging em Python.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa migrações em modo 'offline'.

    Configura o contexto apenas com a URL
    e não cria um Engine; assim não é necessário ter um DBAPI disponível.

    As chamadas a context.execute() aqui emitem a string no
    output do script.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações em modo 'online'.

    Neste cenário criamos um Engine e associamos
    uma conexão ao contexto.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        from sqlalchemy import text
        connection.execute(text('SET search_path TO aican'))
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema='aican'
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
