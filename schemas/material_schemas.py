from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class MaterialBase(BaseModel):
    nombre_material: str
    cantidad: int

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(BaseModel):
    nombre_material: Optional[str] = None
    cantidad: Optional[int] = None

class MaterialResponse(MaterialBase):
    id_material: UUID
    id_empresa: UUID

    class Config:
        from_attributes = True  # Permitir mapeo con ORM

class SolicitudMaterialBase(BaseModel):
    id_material: UUID
    cantidad_solicitada: int

class SolicitudMaterialCreate(BaseModel):
    id_material: UUID
    cantidad_solicitada: int

class SolicitudMaterialUpdate(BaseModel):
    cantidad_solicitada: Optional[int] = None
    estado_solicitud: Optional[str] = None

class SolicitudMaterialResponse(BaseModel):
    id_solicitud: UUID
    nombre_material: str
    cantidad_solicitada: int
    fecha_solicitud: datetime
    estado_solicitud: str
    nombre_empresa: str
    imagen_solicitud: Optional[str] = None

    class Config:
        from_attributes = True 
    
