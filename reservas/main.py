from fastapi import FastAPI, Depends, Query, HTTPException
from db import create_db_and_tables, get_session, Reserva
from sqlmodel import select
from typing import Annotated
from sqlmodel import Session

SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/reservas/")
def get_reservas(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    """Obtener listado de reservas con paginación."""
    reservas = session.exec(select(Reserva).offset(offset).limit(limit)).all()
    return reservas


@app.get("/reservas/{reserva_id}")
def read_hero(reserva_id: int, session: SessionDep):
    """Obtener una reserva por su ID."""
    reserva = session.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


@app.post("/reservas/")
def create_reserva(reserva: Reserva, session: SessionDep):
    """Crear una nueva reserva."""
    session.add(reserva)
    session.commit()
    session.refresh(reserva)
    return reserva


@app.put("/reservas/{reserva_id}")
def update_reserva(reserva_id: int, reserva: Reserva, session: SessionDep):
    """Actualizar una reserva existente."""
    existing_reserva = session.get(Reserva, reserva_id)
    if not existing_reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    for key, value in reserva.dict(exclude_unset=True).items():
        setattr(existing_reserva, key, value)

    session.add(existing_reserva)
    session.commit()
    session.refresh(existing_reserva)
    return existing_reserva
