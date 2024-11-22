from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PublicacionBase(BaseModel):
    id_reciclador: str  # ID del reciclador
    descripcion: str
    imagen_url: Optional[str] = None  # URL de la imagen, opcional
    fecha_creacion: datetime = datetime.utcnow()

class PublicacionResponse(PublicacionBase):
    id: str  # El ID de la publicación en formato de cadena

    class Config:
        orm_mode = True