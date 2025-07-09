from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.reserva import Reserva, ReservaPublic, ReservaBase, ReservaUpdate
from app.models.horario_clase import (
    HorarioClase,
    HorarioClaseCreate,
    HorarioClaseRead,
    HorarioClaseReadWithSesiones,
    HorarioClaseUpdate,
    SesionClase,
    SesionClaseCreate,
    SesionClaseRead,
    SesionClaseUpdate,
    DiaSemana,
    EstadoSesion,
)
from app.db import create_db_and_tables, get_session
from app.filters import (
    ReservaFilterParams,
    HorarioClaseFilterParams,
)
from app.models.equipos_reserva import EquiposReservaBase
from app.constants import StatusReserva
from sqlmodel import select
from typing import Annotated, List
from sqlmodel import Session
import httpx

SessionDep = Annotated[Session, Depends(get_session)]


# Agrega root_path para que FastAPI sepa que está detrás de un prefijo en el Ingress
app = FastAPI(root_path="/api/reservas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}


# --- CRUD para Reservas ---


@app.get("/reservas/", response_model=list[ReservaPublic])
def get_reservas(
    session: SessionDep, filter_query: Annotated[ReservaFilterParams, Depends()]
):
    """Obtener listado de reservas con paginación y filtrado."""
    query = (
        select(Reserva)
        .order_by(getattr(Reserva, filter_query.order_by))
        .offset(filter_query.offset)
        .limit(filter_query.limit)
    )

    # Aplicar filtros
    if filter_query.status:
        query = query.where(Reserva.status == filter_query.status)
    if filter_query.id_laboratorio:
        query = query.where(Reserva.id_ubicacion == filter_query.id_laboratorio)

    reservas = session.exec(query).all()

    # Obtener equipos para cada reserva y sus detalles
    reservas_public = []
    LABS_URL = "http://localhost:8002/equipos/"  # Ajusta el puerto/host si es necesario
    for reserva in reservas:
        equipos_ids = session.exec(
            select(EquiposReservaBase.id_equipo).where(
                EquiposReservaBase.id_reserva == reserva.id
            )
        ).all()
        equipos_detalles = []
        for id_equipo in equipos_ids:
            try:
                with httpx.Client() as client:
                    r = client.get(f"{LABS_URL}{id_equipo}")
                    if r.status_code == 200:
                        equipos_detalles.append(r.json())
            except Exception:
                pass
        reserva_dict = (
            reserva.model_dump() if hasattr(reserva, "model_dump") else reserva.dict()
        )
        reserva_dict["equipos"] = equipos_detalles
        reservas_public.append(ReservaPublic(**reserva_dict))
    return reservas_public


@app.get("/reservas/{reserva_id}", response_model=ReservaPublic)
def read_reserva(reserva_id: int, session: SessionDep):
    """Obtener una reserva por su ID."""
    reserva = session.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    equipos_ids = session.exec(
        select(EquiposReservaBase.id_equipo).where(
            EquiposReservaBase.id_reserva == reserva.id
        )
    ).all()
    equipos_detalles = []
    LABS_URL = "http://localhost:8002/equipos/"  # Ajusta el puerto/host si es necesario
    for id_equipo in equipos_ids:
        try:
            with httpx.Client() as client:
                r = client.get(f"{LABS_URL}{id_equipo}")
                if r.status_code == 200:
                    equipos_detalles.append(r.json())
        except Exception:
            pass
    reserva_dict = (
        reserva.model_dump() if hasattr(reserva, "model_dump") else reserva.dict()
    )
    reserva_dict["equipos"] = equipos_detalles
    return ReservaPublic(**reserva_dict)


@app.post("/reservas/", response_model=ReservaPublic)
def create_reserva(reserva: ReservaBase, session: SessionDep):
    """Crear una nueva reserva."""
    # Validar que no haya un horario de clase conflictivo
    dias_semana_map = {
        0: "lunes",
        1: "martes",
        2: "miercoles",
        3: "jueves",
        4: "viernes",
        5: "sabado",
    }
    dia_semana_reserva = dias_semana_map.get(reserva.fecha_inicio.weekday())

    if dia_semana_reserva:
        conflicting_schedule = session.exec(
            select(SesionClase).where(
                SesionClase.id_ubicacion == reserva.id_ubicacion,
                SesionClase.dia_semana == DiaSemana(dia_semana_reserva),
                SesionClase.estado == EstadoSesion.activa,
                SesionClase.hora_inicio < reserva.fecha_fin.time(),
                SesionClase.hora_fin > reserva.fecha_inicio.time(),
            )
        ).first()

        if conflicting_schedule:
            raise HTTPException(
                status_code=409,
                detail=f"El laboratorio está ocupado por una clase en ese horario ({conflicting_schedule.hora_inicio} - {conflicting_schedule.hora_fin}).",
            )

    # Revisar colisiones entre reservas
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

    db_reserva = Reserva.model_validate(reserva)
    session.add(db_reserva)
    session.commit()
    session.refresh(db_reserva)

    # Guardar equipos asociados a la reserva
    equipos_ids = reserva.equipos or []
    for id_equipo in equipos_ids:
        if db_reserva.id:
            equipo_reserva = EquiposReservaBase(
                id_reserva=db_reserva.id, id_equipo=id_equipo
            )
            session.add(equipo_reserva)
    session.commit()

    # Obtener equipos para la respuesta
    equipos = session.exec(
        select(EquiposReservaBase.id_equipo).where(
            EquiposReservaBase.id_reserva == db_reserva.id
        )
    ).all()
    reserva_dict = (
        db_reserva.model_dump()
        if hasattr(db_reserva, "model_dump")
        else db_reserva.dict()
    )
    reserva_dict["equipos"] = equipos
    return ReservaPublic(**reserva_dict)


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


# --- CRUD para HorarioClase ---


@app.post("/horarios-clase/", response_model=HorarioClaseRead)
def create_horario_clase(horario_data: HorarioClaseCreate, session: SessionDep):
    horario_dict = horario_data.model_dump(exclude={"sesiones"})
    db_horario = HorarioClase(**horario_dict)

    for sesion_data in horario_data.sesiones:
        sesion = SesionClase(**sesion_data.model_dump(), horario_clase=db_horario)
        session.add(sesion)

    session.add(db_horario)
    session.commit()
    session.refresh(db_horario)
    return db_horario


@app.get("/horarios-clase/", response_model=List[HorarioClaseReadWithSesiones])
def get_horarios_clase(
    session: SessionDep, filters: Annotated[HorarioClaseFilterParams, Depends()]
):
    query = (
        select(HorarioClase)
        .order_by(getattr(HorarioClase, filters.order_by))
        .offset(filters.offset)
        .limit(filters.limit)
    )
    if filters.nombre_materia:
        query = query.where(
            HorarioClase.nombre_materia.contains(filters.nombre_materia)
        )
    if filters.id_usuario:
        query = query.where(HorarioClase.id_usuario == filters.id_usuario)

    horarios = session.exec(query).all()
    return horarios


@app.get("/horarios-clase/{horario_id}", response_model=HorarioClaseReadWithSesiones)
def get_horario_clase(horario_id: int, session: SessionDep):
    horario = session.get(HorarioClase, horario_id)
    if not horario:
        raise HTTPException(status_code=404, detail="Horario de clase no encontrado")
    return horario


@app.patch("/horarios-clase/{horario_id}", response_model=HorarioClaseRead)
def update_horario_clase(
    horario_id: int, horario_data: HorarioClaseUpdate, session: SessionDep
):
    db_horario = session.get(HorarioClase, horario_id)
    if not db_horario:
        raise HTTPException(status_code=404, detail="Horario de clase no encontrado")

    update_data = horario_data.model_dump(exclude_unset=True)
    db_horario.sqlmodel_update(update_data)
    session.add(db_horario)
    session.commit()
    session.refresh(db_horario)
    return db_horario


@app.delete("/horarios-clase/{horario_id}", status_code=204)
def delete_horario_clase(horario_id: int, session: SessionDep):
    horario = session.get(HorarioClase, horario_id)
    if not horario:
        raise HTTPException(status_code=404, detail="Horario de clase no encontrado")
    session.delete(horario)
    session.commit()
    return


# --- Endpoints para gestionar Sesiones DENTRO de un Horario ---


@app.post("/horarios-clase/{horario_id}/sesiones/", response_model=SesionClaseRead)
def add_sesion_to_horario(
    horario_id: int, sesion_data: SesionClaseCreate, session: SessionDep
):
    horario = session.get(HorarioClase, horario_id)
    if not horario:
        raise HTTPException(status_code=404, detail="Horario de clase no encontrado")

    sesion_data.id_horario_clase = horario_id
    db_sesion = SesionClase.model_validate(sesion_data)
    session.add(db_sesion)
    session.commit()
    session.refresh(db_sesion)
    return db_sesion


@app.patch("/sesiones-clase/{sesion_id}", response_model=SesionClaseRead)
def update_sesion_clase(
    sesion_id: int, sesion_data: SesionClaseUpdate, session: SessionDep
):
    db_sesion = session.get(SesionClase, sesion_id)
    if not db_sesion:
        raise HTTPException(status_code=404, detail="Sesión de clase no encontrada")

    update_data = sesion_data.model_dump(exclude_unset=True)
    db_sesion.sqlmodel_update(update_data)
    session.add(db_sesion)
    session.commit()
    session.refresh(db_sesion)
    return db_sesion


@app.delete("/sesiones-clase/{sesion_id}", status_code=204)
def delete_sesion_clase(sesion_id: int, session: SessionDep):
    sesion = session.get(SesionClase, sesion_id)
    if not sesion:
        raise HTTPException(status_code=404, detail="Sesión de clase no encontrada")
    session.delete(sesion)
    session.commit()
    return
