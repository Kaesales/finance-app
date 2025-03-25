from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do banco de dados a partir das variáveis de ambiente
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"

# Cria o engine assíncrono
engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)

# Configura a sessão assíncrona
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base para os modelos
Base = declarative_base()

# Função para obter a sessão do banco de dados
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

# Função para criar as tabelas
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)