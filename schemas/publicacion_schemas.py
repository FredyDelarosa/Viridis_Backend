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
    nombre_usuario: Optional[str]  # Nombre del usuario o empresa


class UsuarioResponse(BaseModel):
    id: str
    nombre: str
    email: str
    # Agrega más campos según lo que quieras devolver


    class Config:
        orm_mode = True