from fastapi import FastAPI, Depends, Query, HTTPException
from models.reserva import Reserva, ReservaPublic, ReservaBase, ReservaUpdate
from db import create_db_and_tables, get_session
from sqlmodel import select
from typing import Annotated
from sqlmodel import Session
from filters import ReservaFilterParams
from constants import StatusReserva

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
    session: SessionDep, filter_query: Annotated[ReservaFilterParams, Query()]
):
    """Obtener listado de reservas con paginación y filtrado."""
    query = (
        select(Reserva)
        .order_by(filter_query.order_by)
        .offset(filter_query.offset)
        .limit(filter_query.limit)
    )

    # Aplicar filtros
    if filter_query.status:
        query = query.where(Reserva.status == filter_query.status)
    if filter_query.id_laboratorio:
        query = query.where(Reserva.id_ubicacion == filter_query.id_laboratorio)

    reservas = session.exec(query).all()
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
    """Crear una nueva reserva, evitando colisiones."""
    # Verificar colisión de reservas
    colision = session.exec(
        select(Reserva).where(
            Reserva.id_ubicacion == reserva.id_ubicacion,
            Reserva.status == StatusReserva.COMPLETED,
            Reserva.fecha_inicio < reserva.fecha_fin,
            Reserva.fecha_fin > reserva.fecha_inicio,
        )
    ).first()
    if colision:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una reserva para ese laboratorio y rango de fechas.",
        )
    nueva_reserva = Reserva.model_validate(reserva)
    session.add(nueva_reserva)
    session.commit()
    session.refresh(nueva_reserva)
    return nueva_reserva


@app.patch("/reservas/{reserva_id}", response_model=ReservaPublic)
def update_reserva(reserva_id: int, reserva: ReservaUpdate, session: SessionDep):
    reserva_db = session.get(Reserva, reserva_id)
    if not reserva_db:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    reserva_data = reserva.model_dump(exclude_unset=True)
    reserva_db.sqlmodel_update(reserva_data)
    session.add(reserva_db)
    session.commit()
    session.refresh(reserva_db)
    return reserva_db
