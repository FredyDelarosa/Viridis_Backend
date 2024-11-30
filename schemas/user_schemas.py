from fastapi import Form
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
    imagen_empresa: Optional[str]

#class UsuarioEmpresaCreate(UsuarioEmpresaBase):
    #contraseña: str

class UsuarioEmpresaCreate(BaseModel):
    nombre_empresa: str
    dueño_empresa: str
    direccion: str
    email: str
    telefono: Optional[str]
    estado: str
    ciudad: Optional[str]
    municipio: Optional[str]
    contraseña: str
    imagen_empresa: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        nombre_empresa: str = Form(...),
        dueño_empresa: str = Form(...),
        direccion: str = Form(...),
        email: str = Form(...),
        telefono: str = Form(None),
        estado: str = Form(...),
        ciudad: str = Form(None),
        municipio: str = Form(None),
        contraseña: str = Form(...),
    ):
        return cls(
            nombre_empresa=nombre_empresa,
            dueño_empresa=dueño_empresa,
            direccion=direccion,
            email=email,
            telefono=telefono,
            estado=estado,
            ciudad=ciudad,
            municipio=municipio,
            contraseña=contraseña,
        )

class UsuarioEmpresaResponse(BaseModel):
    id_empresa: UUID    
    nombre_empresa: str
    dueño_empresa: str
    direccion: str
    email: str
    telefono: Optional[str]
    estado: str
    ciudad: Optional[str]
    municipio: Optional[str]
    imagen_empresa: Optional[str]
    estatus: str

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