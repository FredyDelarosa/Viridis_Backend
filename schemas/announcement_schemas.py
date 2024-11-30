from pydantic import BaseModel, HttpUrl
from uuid import UUID
from datetime import datetime
from typing import Optional

class AnuncioBase(BaseModel):
    id_empresa: str
    contenido_anuncio: str

class AnuncioCreate(AnuncioBase):
    pass

class AnuncioResponse(AnuncioBase):
    id_anuncio: str
    imagen_url: Optional[str]
    fecha_publicacion: datetime

    class Config:
        orm_mode = True
