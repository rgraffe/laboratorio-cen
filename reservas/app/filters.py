from pydantic import BaseModel, Field
from typing import Literal
from app.models.horario_clase import DiaSemana, EstadoSesion


class ReservaFilterParams(BaseModel):
    """Parámetros para filtrar reservas."""

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["fecha_creacion", "fecha_inicio"] = "fecha_inicio"
    status: Literal["pending", "confirmed", "cancelled"] | None = None
    id_laboratorio: int | None = None


class HorarioClaseFilterParams(BaseModel):
    """Parámetros para filtrar horarios de clase."""

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["nombre_materia"] = "nombre_materia"
    nombre_materia: str | None = None
    id_usuario: int | None = None


class SesionClaseFilterParams(BaseModel):
    """Parámetros para filtrar sesiones de clase."""

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["dia_semana", "hora_inicio"] = "dia_semana"
    dia_semana: DiaSemana | None = None
    id_ubicacion: int | None = None
    id_horario_clase: int | None = None
    estado: EstadoSesion | None = None

