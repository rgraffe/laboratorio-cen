from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from enum import Enum


class EstadoEquipo(str, Enum):
    OPERATIVO = "Operativo"
    MANTENIMIENTO = "Mantenimiento"
    DAÑADO = "Dañado"


# --- Modelo para Equipo ---
class EquipoBase(SQLModel):
    nombre: str = Field(index=True)
    modelo: str
    estado: EstadoEquipo = Field(default=EstadoEquipo.OPERATIVO)
    id_laboratorio: Optional[int] = Field(default=None, foreign_key="laboratorio.id")


class Equipo(EquipoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    laboratorio: "Laboratorio" = Relationship(back_populates="equipos")


# --- Modelo para Laboratorio ---
class LaboratorioBase(SQLModel):
    nombre: str = Field(index=True, unique=True)
    descripcion: str


class Laboratorio(LaboratorioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    equipos: List["Equipo"] = Relationship(
        back_populates="laboratorio", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# --- Esquemas para la API ---

# Esquemas de Equipo
class EquipoRead(EquipoBase):
    id: int

class EquipoCreate(EquipoBase):
    pass

class EquipoUpdate(SQLModel):
    nombre: Optional[str] = None
    modelo: Optional[str] = None
    estado: Optional[EstadoEquipo] = None
    id_laboratorio: Optional[int] = None


# Esquemas de Laboratorio
class LaboratorioRead(LaboratorioBase):
    id: int

class LaboratorioCreate(LaboratorioBase):
    pass

class LaboratorioUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class LaboratorioReadWithEquipos(LaboratorioRead):
    equipos: List[EquipoRead] = []

class EquipoReadWithLaboratorio(EquipoRead):
    laboratorio: Optional[LaboratorioRead] = None
