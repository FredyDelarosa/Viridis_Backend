# app/routers/announcement_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from db.database import get_db
from schemas.announcement_schemas import (AnuncioCreate, AnuncioUpdate,AnuncioResponse)
from crud.announcement_crud import (create_anuncio, get_anuncio, get_anuncios, update_anuncio, delete_anuncio)

router = APIRouter()

@router.post("/anuncios", response_model=AnuncioResponse)
def create_anuncio_route(id_empresa: UUID, anuncio: AnuncioCreate, db: Session = Depends(get_db)):
    return create_anuncio(db, anuncio, id_empresa)

@router.get("/anuncios/{anuncio_id}", response_model=AnuncioResponse)
def read_anuncio(anuncio_id: UUID, db: Session = Depends(get_db)):
    db_anuncio = get_anuncio(db, anuncio_id)
    if db_anuncio is None:
        raise HTTPException(status_code=404, detail="Anuncio no encontrado")
    return db_anuncio

@router.get("/anuncios", response_model=list[AnuncioResponse])
def read_anuncios(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_anuncios(db, skip=skip, limit=limit)

@router.put("/anuncios/{anuncio_id}", response_model=AnuncioResponse)
def update_anuncio_route(anuncio_id: UUID, anuncio: AnuncioUpdate, db: Session = Depends(get_db)):
    db_anuncio = update_anuncio(db, anuncio_id, anuncio)
    if db_anuncio is None:
        raise HTTPException(status_code=404, detail="Anuncio no encontrado")
    return db_anuncio

@router.delete("/anuncios/{anuncio_id}", response_model=AnuncioResponse)
def delete_anuncio_route(anuncio_id: UUID, db: Session = Depends(get_db)):
    db_anuncio = delete_anuncio(db, anuncio_id)
    if db_anuncio is None:
        raise HTTPException(status_code=404, detail="Anuncio no encontrado")
    return db_anuncio
