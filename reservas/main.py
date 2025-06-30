from fastapi import FastAPI, Depends, Query, HTTPException
from models.reserva import Reserva, ReservaPublic, ReservaBase, ReservaUpdate
from db import create_db_and_tables, get_session
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


@app.get("/reservas/", response_model=list[ReservaPublic])
def get_reservas(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    """Obtener listado de reservas con paginación."""
    reservas = session.exec(select(Reserva).offset(offset).limit(limit)).all()
    return reservas


@app.get("/reservas/{reserva_id}", response_model=ReservaPublic)
def read_hero(reserva_id: int, session: SessionDep):
    """Obtener una reserva por su ID."""
    reserva = session.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva


@app.post("/reservas/", response_model=ReservaPublic)
def create_reserva(reserva: ReservaBase, session: SessionDep):
    """Crear una nueva reserva."""
    session.add(reserva)
    session.commit()
    session.refresh(reserva)
    return reserva


@app.patch("/reservas/{reserva_id}", response_model=ReservaPublic)
def update_hero(reserva_id: int, reserva: ReservaUpdate, session: SessionDep):
    reserva_db = session.get(Reserva, reserva_id)
    if not reserva_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = reserva.model_dump(exclude_unset=True)
    reserva_db.sqlmodel_update(hero_data)
    session.add(reserva_db)
    session.commit()
    session.refresh(reserva_db)
    return reserva_db
