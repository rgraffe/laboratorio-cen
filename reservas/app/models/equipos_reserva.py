from sqlmodel import Field, SQLModel


class EquiposReservaBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    id_reserva: int = Field(foreign_key="reserva.id")
    id_equipo: int
