# app/crud/announcement_crud.py
from sqlalchemy.orm import Session
from uuid import UUID
from models.announcemente_model import Anuncio
from schemas.announcement_schemas import AnuncioCreate, AnuncioUpdate

def create_anuncio(db: Session, anuncio_data: AnuncioCreate, id_empresa: UUID):
    db_anuncio = Anuncio(
        id_empresa=id_empresa,
        contenido_anuncio=anuncio_data.contenido_anuncio,
        imagen_url=anuncio_data.imagen_url
    )
    db.add(db_anuncio)
    db.commit()
    db.refresh(db_anuncio)
    return db_anuncio

def get_anuncio(db: Session, anuncio_id: UUID):
    return db.query(Anuncio).filter(Anuncio.id_anuncio == anuncio_id).first()

def get_anuncios(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Anuncio).offset(skip).limit(limit).all()

def update_anuncio(db: Session, anuncio_id: UUID, anuncio_data: AnuncioUpdate):
    db_anuncio = get_anuncio(db, anuncio_id)
    if db_anuncio:
        if anuncio_data.contenido_anuncio is not None:
            db_anuncio.contenido_anuncio = anuncio_data.contenido_anuncio
        if anuncio_data.imagen_url is not None:
            db_anuncio.imagen_url = anuncio_data.imagen_url
        db.commit()
        db.refresh(db_anuncio)
    return db_anuncio

def delete_anuncio(db: Session, anuncio_id: UUID):
    db_anuncio = get_anuncio(db, anuncio_id)
    if db_anuncio:
        db.delete(db_anuncio)
        db.commit()
    return db_anuncio
