from datetime import datetime
from sqlmodel import Field, Session, SQLModel, create_engine
import os


class Reserva(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_inicio: datetime = Field()
    fecha_fin: datetime = Field()
    id_usuario: int = Field()
    id_ubicacion: int = Field()
    id_equipo: int | None = Field(default=None)
    status: str = Field(
        default="pending", sa_column_kwargs={"server_default": "pending"}
    )


postgres_url = os.getenv(
    "DB_URL", "postgresql://username:password@localhost:5432/database_name"
)

engine = create_engine(postgres_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
