from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime
from typing import Optional

class AnuncioBase(BaseModel):
    contenido_anuncio: str
    imagen_url: Optional[HttpUrl] = None

class AnuncioCreate(AnuncioBase):
    pass

class AnuncioUpdate(BaseModel):
    contenido_anuncio: Optional[str] = None
    imagen_url: Optional[HttpUrl] = None

class AnuncioResponse(AnuncioBase):
    id_anuncio: UUID
    id_empresa: UUID
    fecha_publicacion: datetime

    class Config:
        from_attributes = True  # Configuración para permitir ORM
