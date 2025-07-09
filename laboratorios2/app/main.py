from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List, Annotated
from app.db import get_session, create_db_and_tables
from app.models.laboratorio import (
    Laboratorio,
    LaboratorioCreate,
    LaboratorioRead,
    LaboratorioUpdate,
    LaboratorioReadWithEquipos,
    Equipo,
    EquipoCreate,
    EquipoRead,
    EquipoUpdate,
    EquipoReadWithLaboratorio,
)
from app.filters import LaboratorioFilterParams, EquipoFilterParams

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(root_path="/api/laboratorios")

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


# --- CRUD para Laboratorios ---


@app.post("/laboratorios/", response_model=LaboratorioRead)
def create_laboratorio(laboratorio: LaboratorioCreate, session: SessionDep):
    db_laboratorio = Laboratorio.model_validate(laboratorio)
    session.add(db_laboratorio)
    session.commit()
    session.refresh(db_laboratorio)
    return db_laboratorio


@app.get("/laboratorios/", response_model=List[LaboratorioRead])
def get_laboratorios(
    session: SessionDep, filters: Annotated[LaboratorioFilterParams, Depends()]
):
    query = (
        select(Laboratorio)
        .offset(filters.offset)
        .limit(filters.limit)
        .order_by(getattr(Laboratorio, filters.order_by))
    )
    if filters.nombre:
        query = query.where(Laboratorio.nombre.contains(filters.nombre))
    laboratorios = session.exec(query).all()
    return laboratorios


@app.get("/laboratorios/{laboratorio_id}", response_model=LaboratorioReadWithEquipos)
def get_laboratorio(laboratorio_id: int, session: SessionDep):
    laboratorio = session.get(Laboratorio, laboratorio_id)
    if not laboratorio:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    return laboratorio


@app.patch("/laboratorios/{laboratorio_id}", response_model=LaboratorioRead)
def update_laboratorio(
    laboratorio_id: int, laboratorio: LaboratorioUpdate, session: SessionDep
):
    db_laboratorio = session.get(Laboratorio, laboratorio_id)
    if not db_laboratorio:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    laboratorio_data = laboratorio.model_dump(exclude_unset=True)
    db_laboratorio.sqlmodel_update(laboratorio_data)
    session.add(db_laboratorio)
    session.commit()
    session.refresh(db_laboratorio)
    return db_laboratorio


@app.delete("/laboratorios/{laboratorio_id}", status_code=204)
def delete_laboratorio(laboratorio_id: int, session: SessionDep):
    laboratorio = session.get(Laboratorio, laboratorio_id)
    if not laboratorio:
        raise HTTPException(status_code=404, detail="Laboratorio no encontrado")
    session.delete(laboratorio)
    session.commit()
    return


# --- CRUD para Equipos ---


@app.post("/equipos/", response_model=EquipoRead)
def create_equipo(equipo: EquipoCreate, session: SessionDep):
    db_equipo = Equipo.model_validate(equipo)
    session.add(db_equipo)
    session.commit()
    session.refresh(db_equipo)
    return db_equipo


@app.get("/equipos/", response_model=List[EquipoRead])
def get_equipos(session: SessionDep, filters: Annotated[EquipoFilterParams, Depends()]):
    query = (
        select(Equipo)
        .offset(filters.offset)
        .limit(filters.limit)
        .order_by(getattr(Equipo, filters.order_by))
    )
    if filters.estado:
        query = query.where(Equipo.estado == filters.estado)
    if filters.id_laboratorio:
        query = query.where(Equipo.id_laboratorio == filters.id_laboratorio)
    equipos = session.exec(query).all()
    return equipos


@app.get("/equipos/{equipo_id}", response_model=EquipoReadWithLaboratorio)
def get_equipo(equipo_id: int, session: SessionDep):
    equipo = session.get(Equipo, equipo_id)
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return equipo


@app.patch("/equipos/{equipo_id}", response_model=EquipoRead)
def update_equipo(equipo_id: int, equipo: EquipoUpdate, session: SessionDep):
    db_equipo = session.get(Equipo, equipo_id)
    if not db_equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    equipo_data = equipo.model_dump(exclude_unset=True)
    db_equipo.sqlmodel_update(equipo_data)
    session.add(db_equipo)
    session.commit()
    session.refresh(db_equipo)
    return db_equipo


@app.delete("/equipos/{equipo_id}", status_code=204)
def delete_equipo(equipo_id: int, session: SessionDep):
    equipo = session.get(Equipo, equipo_id)
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    session.delete(equipo)
    session.commit()
    return
