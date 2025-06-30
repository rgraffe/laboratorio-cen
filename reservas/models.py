from pydantic import BaseModel
from typing import Literal
from constants import StatusReserva


class Reserva(BaseModel):
    id: int
    fecha_creacion: str
    fecha_inicio: str
    fecha_fin: str
    id_usuario: int
    id_ubicacion: int
    id_equipo: int | None = None
    status: Literal["completed", "pending", "cancelled"] = StatusReserva.PENDING
