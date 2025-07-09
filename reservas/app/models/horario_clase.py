from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import time
from enum import Enum


class DiaSemana(str, Enum):
    lunes = "lunes"
    martes = "martes"
    miercoles = "miercoles"
    jueves = "jueves"
    viernes = "viernes"
    sabado = "sabado"


class EstadoSesion(str, Enum):
    activa = "activa"
    cancelada = "cancelada"


# --- Modelo para la Sesión de Clase (el bloque horario específico) ---

class SesionClaseBase(SQLModel):
    dia_semana: DiaSemana
    hora_inicio: time
    hora_fin: time
    id_ubicacion: int = Field(index=True)
    estado: EstadoSesion = Field(default=EstadoSesion.activa)
    id_horario_clase: Optional[int] = Field(default=None, foreign_key="horarioclase.id")


class SesionClase(SesionClaseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    horario_clase: "HorarioClase" = Relationship(back_populates="sesiones")


# --- Modelo para el Horario de Clase (la materia o curso general) ---

class HorarioClaseBase(SQLModel):
    nombre_materia: str = Field(index=True)
    # ID del profesor (tratado como un entero, sin relación de BD)
    id_usuario: int = Field(index=True)


class HorarioClase(HorarioClaseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sesiones: List["SesionClase"] = Relationship(
        back_populates="horario_clase", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# --- Esquemas para la API (lectura, creación y actualización) ---

class SesionClaseRead(SesionClaseBase):
    id: int

class HorarioClaseRead(HorarioClaseBase):
    id: int

class HorarioClaseReadWithSesiones(HorarioClaseRead):
    sesiones: List[SesionClaseRead] = []


# Esquema para crear una sesión (hereda de la base)
class SesionClaseCreate(SesionClaseBase):
    pass


# Esquema para crear una sesión DENTRO de un horario
class SesionClaseForCreate(SQLModel):
    dia_semana: DiaSemana
    hora_inicio: time
    hora_fin: time
    id_ubicacion: int
    estado: EstadoSesion = Field(default=EstadoSesion.activa)

# Esquema para crear un HorarioClase con sus sesiones iniciales
class HorarioClaseCreate(HorarioClaseBase):
    sesiones: List[SesionClaseForCreate] = []

# Esquemas para actualización
class HorarioClaseUpdate(SQLModel):
    nombre_materia: Optional[str] = None
    id_usuario: Optional[int] = None

class SesionClaseUpdate(SQLModel):
    dia_semana: Optional[DiaSemana] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    id_ubicacion: Optional[int] = None
    estado: Optional[EstadoSesion] = None