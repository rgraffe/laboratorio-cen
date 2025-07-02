from pydantic import BaseModel, Field
from typing import Literal


class ReservaFilterParams(BaseModel):
    """Parámetros para filtrar reservas."""

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["fecha_creacion", "fecha_inicio"] = "fecha_inicio"
    status: Literal["pending", "confirmed", "cancelled"] | None = None
    id_laboratorio: int | None = None
