import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Lê as variáveis do arquivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não foi configurada no arquivo .env."
    )

# Garante o uso do driver psycopg 3
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )

# Cria a conexão com o banco
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Cria sessões para executar operações no banco
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# Classe-base para os modelos do banco
Base = declarative_base()


# Fornece uma sessão para cada requisição
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
