# app/routers/publicacion_routes.py
from datetime import datetime
import os
from uuid import uuid4
from bson import ObjectId
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from requests import Session
from sqlalchemy import text
from schemas.publicacion_schemas import PublicacionBase, PublicacionResponse
from db.database import get_db, publicaciones_collection


router = APIRouter()

UPLOAD_FOLDER = "uploads/publicaciones"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Agrega la URL completa del servidor para las imágenes
BASE_URL = "http://localhost:8000"

@router.post("/", response_model=PublicacionResponse, status_code=201)
async def crear_publicacion(
    id_usuario: str = Form(...),
    descripcion: str = Form(...),
    file: UploadFile = File(...),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Guardar la imagen
    filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Devuelve la URL completa para las imágenes
    image_url = f"{BASE_URL}/uploads/publicaciones/{filename}"

    nueva_publicacion = {
        "id_usuario": id_usuario,
        "descripcion": descripcion,
        "imagen_url": image_url,
        "fecha_creacion": datetime.utcnow(),
    }
    result = await publicaciones_collection.insert_one(nueva_publicacion)
    nueva_publicacion["id"] = str(result.inserted_id)

    return nueva_publicacion

async def get_user_name(id_usuario: str, db: Session):
    # Consulta en la tabla de recicladores
    reciclador_query = f"SELECT usuario FROM usuario_reciclador WHERE id_reciclador = '{id_usuario}'"
    reciclador_result = db.execute(text(reciclador_query)).fetchone()
    if reciclador_result:
        return reciclador_result[0]

    # Consulta en la tabla de empresas
    empresa_query = f"SELECT nombre_empresa FROM usuario_empresa WHERE id_empresa = '{id_usuario}'"
    empresa_result = db.execute(text(empresa_query)).fetchone()
    if empresa_result:
        return empresa_result[0]

    # Si no se encuentra en ninguna tabla
    return "Usuario desconocido"


@router.get("/", response_model=list[PublicacionResponse], status_code=200)
async def obtener_todas_las_publicaciones(db: Session = Depends(get_db)):
    publicaciones = []
    async for publicacion in publicaciones_collection.find().sort("fecha_creacion", -1):
        publicacion["id"] = str(publicacion["_id"])
        del publicacion["_id"]

        # Obtener el nombre del usuario según su tipo
        publicacion["nombre_usuario"] = await get_user_name(publicacion["id_usuario"], db)
        
        publicaciones.append(publicacion)
    return publicaciones



@router.get("/user", response_model=list[PublicacionResponse], status_code=200)
async def obtener_publicaciones_por_usuario(id_usuario: str, db: Session = Depends(get_db)):
    publicaciones = []
    async for publicacion in publicaciones_collection.find({"id_usuario": id_usuario}).sort("fecha_creacion", -1):
        publicacion["id"] = str(publicacion["_id"])
        del publicacion["_id"]

        # Agregar el nombre del usuario basado en el tipo
        publicacion["nombre_usuario"] = await get_user_name(id_usuario, db)

        publicaciones.append(publicacion)
    return publicaciones



@router.put("/{id_publicacion}", status_code=200)
async def editar_publicacion(id_publicacion: str, publicacion: PublicacionBase):
    if not ObjectId.is_valid(id_publicacion):
        raise HTTPException(status_code=400, detail="ID de publicación inválido")

    # Verifica si la publicación existe
    publicacion_existente = await publicaciones_collection.find_one({"_id": ObjectId(id_publicacion)})
    if not publicacion_existente:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")

    # Verifica si el usuario tiene permiso para editar
    if publicacion_existente["id_usuario"] != publicacion.id_usuario:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar esta publicación")

    # Realiza la actualización
    resultado = await publicaciones_collection.update_one(
        {"_id": ObjectId(id_publicacion)},
        {"$set": {"descripcion": publicacion.descripcion}}
    )

    if resultado.modified_count == 0:
        raise HTTPException(status_code=400, detail="No se pudo actualizar la publicación")

    return {"message": "Publicación actualizada correctamente"}

@router.delete("/{id_publicacion}", status_code=200)
async def eliminar_publicacion(id_publicacion: str, user_id: str):
    # Verifica que el ID sea válido
    if not ObjectId.is_valid(id_publicacion):
        raise HTTPException(status_code=400, detail="ID de publicación inválido")

    # Busca la publicación
    publicacion = await publicaciones_collection.find_one({"_id": ObjectId(id_publicacion)})
    if not publicacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")

    # Verifica que el usuario tenga permiso para eliminarla
    if publicacion["id_usuario"] != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta publicación")

    # Elimina la publicación
    resultado = await publicaciones_collection.delete_one({"_id": ObjectId(id_publicacion)})

    if resultado.deleted_count == 0:
        raise HTTPException(status_code=400, detail="No se pudo eliminar la publicación")

    return {"message": "Publicación eliminada correctamente"}

