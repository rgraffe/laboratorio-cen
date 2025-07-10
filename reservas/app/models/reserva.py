from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional


class ReservaBase(SQLModel):
    fecha_creacion: datetime | None = Field(default_factory=datetime.utcnow)
    fecha_inicio: datetime = Field()
    fecha_fin: datetime = Field()
    id_usuario: int = Field()
    id_ubicacion: int = Field(index=True)
    status: str = Field(
        default="pending", sa_column_kwargs={"server_default": "pending"}
    )


class Reserva(ReservaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class CreateReserva(ReservaBase):
    id: None = None
    equipos: Optional[list[int]] = None


class ReservaPublic(ReservaBase):
    id: int
    equipos: Optional[list] = None


class ReservaUpdate(ReservaBase):
    id: int
    fecha_creacion: None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    id_usuario: None = None
    id_ubicacion: None = None
    status: str | None = None
