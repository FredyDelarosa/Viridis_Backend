# app/routers/publicacion_routes.py
from fastapi import APIRouter
from schemas.publicacion_schemas import PublicacionBase, PublicacionResponse
from db.database import publicaciones_collection
from typing import List

router = APIRouter()

@router.post("/", response_model=PublicacionResponse)
async def crear_publicacion(publicacion: PublicacionBase):
    publicacion_dict = publicacion.dict()
    result = await publicaciones_collection.insert_one(publicacion_dict)
    
    # Convertir el _id de MongoDB a un campo id para cumplir con el esquema de respuesta
    publicacion_dict["id"] = str(result.inserted_id)
    del publicacion_dict["_id"]  # Eliminar _id de MongoDB de la respuesta final
    
    return publicacion_dict

@router.get("/", response_model=List[PublicacionResponse])
async def obtener_publicaciones():
    publicaciones = []
    async for publicacion in publicaciones_collection.find():
        # Convertir _id a id en cada documento
        publicacion["id"] = str(publicacion["_id"])
        del publicacion["_id"]  # Eliminar _id original de MongoDB
        publicaciones.append(publicacion)
    return publicaciones
