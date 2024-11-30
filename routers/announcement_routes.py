# app/routers/announcement_routes.py
import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from db.database import get_db
from models.announcemente_model import Anuncio
from models.user_models import UsuarioEmpresa
from schemas.announcement_schemas import (AnuncioResponse)
from datetime import datetime

router = APIRouter()

UPLOAD_FOLDER = "uploads/anuncios"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/", response_model=AnuncioResponse, status_code=201)
async def crear_anuncio(
    id_empresa: UUID = Form(...),  # Cambia str por UUID
    contenido_anuncio: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Lógica del endpoint
    empresa = db.query(UsuarioEmpresa).filter(UsuarioEmpresa.id_empresa == id_empresa).first()
    if not empresa:
        raise HTTPException(
            status_code=400,
            detail="La empresa especificada no existe."
        )

    # Verificar que el archivo es una imagen
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Guardar la imagen
    filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join("uploads/anuncios", filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    image_url = f"/uploads/anuncios/{filename}"

    # Crear el anuncio en la base de datos
    nuevo_anuncio = Anuncio(
        id_anuncio=uuid4(),
        id_empresa=id_empresa,
        contenido_anuncio=contenido_anuncio,
        imagen_url=image_url,
        fecha_publicacion=datetime.utcnow()
    )
    db.add(nuevo_anuncio)
    db.commit()
    db.refresh(nuevo_anuncio)

    # Construir el esquema de respuesta
    return {
        "id_anuncio": str(nuevo_anuncio.id_anuncio),  # Conversión explícita a cadena
        "id_empresa": str(nuevo_anuncio.id_empresa),  # Conversión explícita a cadena
        "contenido_anuncio": nuevo_anuncio.contenido_anuncio,
        "imagen_url": nuevo_anuncio.imagen_url,
        "fecha_publicacion": nuevo_anuncio.fecha_publicacion
    }



@router.get("/", response_model=list[AnuncioResponse], status_code=200)
def obtener_anuncios(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    anuncios = db.query(Anuncio).offset(skip).limit(limit).all()

    # Convertir los UUIDs a cadenas
    response = [
        {
            "id_anuncio": str(anuncio.id_anuncio),
            "id_empresa": str(anuncio.id_empresa),
            "contenido_anuncio": anuncio.contenido_anuncio,
            "imagen_url": anuncio.imagen_url,
            "fecha_publicacion": anuncio.fecha_publicacion
        }
        for anuncio in anuncios
    ]

    return response

