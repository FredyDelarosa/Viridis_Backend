# app/routers/user_routes.py
import os
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from auth import get_password_hash
from db.database import get_db
from middlewares.auth_middleware import get_current_user
from models.user_models import UsuarioEmpresa, UsuarioAdministrador
from schemas.user_schemas import UsuarioAdministradorCreate, UsuarioAdministradorResponse, UsuarioEmpresaCreate, UsuarioEmpresaResponse, UsuarioRecicladorCreate, UsuarioRecicladorResponse, UsuarioAdministradorUpdate
from crud.user_crud import create_usuario_administrador, create_usuario_empresa, create_usuario_reciclador, delete_usuario_administrador, delete_usuario_reciclador, get_usuario_administrador, get_usuario_empresa, get_usuario_reciclador, get_usuarios_recicladores, update_usuario_empresa, delete_usuario_empresa

router = APIRouter()

UPLOAD_FOLDER = "uploads/empresas"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

"""
@router.post("/empresa", response_model=UsuarioEmpresaResponse)
def create_empresa(usuario: UsuarioEmpresaCreate, db: Session = Depends(get_db)):
    return create_usuario_empresa(db, usuario)
"""

@router.post("/empresa", response_model=UsuarioEmpresaResponse)
async def create_empresa(
    usuario: UsuarioEmpresaCreate = Depends(UsuarioEmpresaCreate.as_form),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Verificar que no exista una empresa con el mismo email
    if db.query(UsuarioEmpresa).filter(UsuarioEmpresa.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # Guardar la imagen
    filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Crear usuario empresa
    usuario.imagen_empresa = f"/uploads/empresas/{filename}"
    return create_usuario_empresa(db, usuario)


@router.get("/empresa/{empresa_id}", response_model=UsuarioEmpresaResponse)
def read_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    db_empresa = get_usuario_empresa(db, empresa_id)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return db_empresa

@router.get("/empresas", response_model=list[UsuarioEmpresaResponse])
def read_empresas(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.tipo_usuario != "Empresa":
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta ruta")

@router.put("/empresa/{empresa_id}", response_model=UsuarioEmpresaResponse)
def update_empresa(empresa_id: UUID, usuario: UsuarioEmpresaCreate, db: Session = Depends(get_db)):
    db_empresa = update_usuario_empresa(db, empresa_id, usuario)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return db_empresa

@router.delete("/empresa/{empresa_id}", response_model=UsuarioEmpresaResponse)
def delete_empresa(empresa_id: UUID, db: Session = Depends(get_db)):
    db_empresa = delete_usuario_empresa(db, empresa_id)
    if db_empresa is None:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return db_empresa

@router.get("/empresas/pendientes", response_model=List[UsuarioEmpresaResponse])
def obtener_empresas_pendientes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    empresas = (
        db.query(UsuarioEmpresa)
        .filter(UsuarioEmpresa.estatus == "pendiente")
        .offset(skip)
        .limit(limit)
        .all()
    )
    return empresas

@router.post("/empresas/{id_empresa}/aprobar", response_model=UsuarioEmpresaResponse)
def aprobar_empresa(
    id_empresa: str,
    db: Session = Depends(get_db),
):
    # Buscar la empresa
    empresa = db.query(UsuarioEmpresa).filter(UsuarioEmpresa.id_empresa == id_empresa).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    if empresa.estatus == "aprobada":
        raise HTTPException(status_code=400, detail="La empresa ya está aprobada")

    # Cambiar el estatus
    empresa.estatus = "aprobada"
    db.commit()
    db.refresh(empresa)
    return empresa

@router.post("/empresas/{id_empresa}/rechazar", response_model=UsuarioEmpresaResponse)
def rechazar_empresa(
    id_empresa: str,
    db: Session = Depends(get_db),
):
    # Buscar la empresa
    empresa = db.query(UsuarioEmpresa).filter(UsuarioEmpresa.id_empresa == id_empresa).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    if empresa.estatus == "rechazada":
        raise HTTPException(status_code=400, detail="La empresa ya está rechazada")

    # Cambiar el estatus
    empresa.estatus = "rechazada"
    db.commit()
    db.refresh(empresa)
    return empresa

@router.post("/reciclador", response_model=UsuarioRecicladorResponse)
def create_reciclador(usuario: UsuarioRecicladorCreate, db: Session = Depends(get_db)):
    return create_usuario_reciclador(db, usuario)

@router.get("/reciclador/{reciclador_id}", response_model=UsuarioRecicladorResponse)
def read_reciclador(reciclador_id: UUID, db: Session = Depends(get_db)):
    db_reciclador = get_usuario_reciclador(db, reciclador_id)
    if db_reciclador is None:
        raise HTTPException(status_code=404, detail="Reciclador no encontrado")
    return db_reciclador

@router.get("/recicladores", response_model=list[UsuarioRecicladorResponse])
def read_recicladores(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_usuarios_recicladores(db, skip=skip, limit=limit)

@router.delete("/reciclador/{reciclador_id}", response_model=UsuarioRecicladorResponse)
def delete_reciclador(reciclador_id: UUID, db: Session = Depends(get_db)):
    db_reciclador = delete_usuario_reciclador(db, reciclador_id)
    if db_reciclador is None:
        raise HTTPException(status_code=404, detail="Reciclador no encontrado")
    return db_reciclador


@router.post("/administrador", response_model=UsuarioAdministradorResponse)
def create_administrador(usuario: UsuarioAdministradorCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.tipo_usuario != "administrador":
        raise HTTPException(status_code=403, detail="No tienes permisos para realizar esta acción")
    return create_usuario_administrador(db, usuario)

@router.get("/administrador/{administrador_id}", response_model=UsuarioAdministradorResponse)
def read_administrador(administrador_id: UUID, db: Session = Depends(get_db)):
    db_administrador = get_usuario_administrador(db, administrador_id)
    if db_administrador is None:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    return db_administrador

@router.get("/administradores", response_model=list[UsuarioAdministradorResponse])
def read_administradores(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.tipo_usuario != "administrador":
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a esta ruta")
    
    administradores = db.query(UsuarioAdministrador).offset(skip).limit(limit).all()
    if not administradores:
        return []  # Asegúrate de devolver una lista vacía si no hay administradores

    return administradores


@router.delete("/administrador/{administrador_id}", response_model=UsuarioAdministradorResponse)
def delete_administrador(administrador_id: UUID, db: Session = Depends(get_db)):
    db_administrador = delete_usuario_administrador(db, administrador_id)
    if db_administrador is None:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    return db_administrador

@router.put("/administradores/{id_administrador}", response_model=UsuarioAdministradorResponse)
def update_administrador(
    id_administrador: UUID,
    administrador: UsuarioAdministradorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.tipo_usuario != "administrador":
        raise HTTPException(status_code=403, detail="No tienes permiso para esta acción")

    db_administrador = db.query(UsuarioAdministrador).filter(UsuarioAdministrador.id_administrador == id_administrador).first()
    if not db_administrador:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")

    # Extraer solo los campos enviados
    update_data = administrador.dict(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar.")

    for field, value in update_data.items():
        setattr(db_administrador, field, value)

    db.commit()
    db.refresh(db_administrador)

    return db_administrador

