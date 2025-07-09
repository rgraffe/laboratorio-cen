from sqlmodel import Session, SQLModel, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

postgres_url = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/laboratorios_db"
)

engine = create_engine(postgres_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
