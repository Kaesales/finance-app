from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
import os
import sys

# Adicione o caminho do seu projeto ao sys.path
sys.path.append(os.getcwd())

# Importe sua Base e seus modelos
from app.models.base import Base
from app.models.user_model import User
from app.models.account_model import Account
# Configurações do Alembic
config = context.config

# Configura a URL do banco de dados a partir do .env
DATABASE_URL = os.getenv("DATABASE_URL")
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Configura o target_metadata para apontar para a Base
target_metadata = Base.metadata

def do_run_migrations(connection):
    """Executa as migrações usando a conexão fornecida."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Executa migrações no modo online (assíncrono)."""
    # Cria uma engine assíncrona
    connectable = create_async_engine(DATABASE_URL)

    # Conecta ao banco de dados e executa as migrações
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    # Modo offline (síncrono)
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
else:
    # Modo online (assíncrono)
    asyncio.run(run_migrations_online())