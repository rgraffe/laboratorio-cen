from pydantic import BaseModel, Field
from typing import Literal, Optional
from app.models.laboratorio import EstadoEquipo


class LaboratorioFilterParams(BaseModel):
    """Parámetros para filtrar laboratorios."""

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["nombre"] = "nombre"
    nombre: Optional[str] = None


class EquipoFilterParams(BaseModel):
    """Parámetros para filtrar equipos."""

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["nombre"] = "nombre"
    estado: Optional[EstadoEquipo] = None
    id_laboratorio: Optional[int] = None
