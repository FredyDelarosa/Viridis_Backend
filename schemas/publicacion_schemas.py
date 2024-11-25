from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PublicacionBase(BaseModel):
    id_usuario: str
    descripcion: str

class PublicacionCreate(PublicacionBase):
    pass

class PublicacionResponse(PublicacionBase):
    id: str
    imagen_url: Optional[str]
    fecha_creacion: datetime

    class Config:
        orm_mode = True