from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

class UsuarioEmpresaBase(BaseModel):
    nombre_empresa: str
    dueño_empresa: str
    direccion: str
    email: EmailStr
    telefono: Optional[str] = None
    estado: str
    ciudad: Optional[str] = None
    municipio: Optional[str] = None

class UsuarioEmpresaCreate(UsuarioEmpresaBase):
    contraseña: str

class UsuarioEmpresaResponse(BaseModel):
    id_empresa: str
    nombre_empresa: str
    dueño_empresa: str
    direccion: str
    email: str
    telefono: Optional[str]
    estado: str
    ciudad: Optional[str]
    municipio: Optional[str]
    imagen_empresa: Optional[str]

    class Config:
        orm_mode = True


class UsuarioRecicladorBase(BaseModel):
    usuario: str
    email: EmailStr

class UsuarioRecicladorCreate(UsuarioRecicladorBase):
    contraseña: str

class UsuarioRecicladorResponse(UsuarioRecicladorBase):
    id_reciclador: UUID

    class Config:
        from_attributes = True 


class UsuarioAdministradorBase(BaseModel):
    usuario: str
    email: EmailStr

class UsuarioAdministradorCreate(UsuarioAdministradorBase):
    contraseña: str

class UsuarioAdministradorResponse(UsuarioAdministradorBase):
    id_administrador: UUID
    contraseña: Optional[str] = "********"
    
class UsuarioAdministradorUpdate(BaseModel):
    usuario: Optional[str]  # Opcional
    email: Optional[EmailStr]  # Opcional

    class Config:
        from_attributes = True