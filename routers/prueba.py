# app/routers/user_routes.py
import os
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
@router.post("/", response_model=UsuarioEmpresaResponse, status_code=201)
async def crear_usuario_empresa(
    nombre_empresa: str = Form(...),
    dueño_empresa: str = Form(...),
    direccion: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(None),
    estado: str = Form(...),
    ciudad: str = Form(None),
    municipio: str = Form(None),
    contraseña: str = Form(...),
    file: UploadFile = File(...),  # Imagen de prueba de la empresa
    db: Session = Depends(get_db)
):
    # Verificar que no exista una empresa con el mismo email
    if db.query(UsuarioEmpresa).filter(UsuarioEmpresa.email == email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # Guardar la imagen
    filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    image_url = f"/uploads/empresas/{filename}"  # Ruta relativa para la imagen

    # Crear el usuario empresa
    nueva_empresa = UsuarioEmpresa(
        id_empresa=str(uuid4()),
        nombre_empresa=nombre_empresa,
        dueño_empresa=dueño_empresa,
        direccion=direccion,
        email=email,
        telefono=telefono,
        estado=estado,
        ciudad=ciudad,
        municipio=municipio,
        contraseña=contraseña,  # Considera encriptar esta contraseña
        imagen_empresa=image_url
    )
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)

    return nueva_empresa

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

    # Solo actualiza los campos enviados
    update_data = administrador.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "contraseña":
            value = get_password_hash(value)  # Hash para contraseñas
        setattr(db_administrador, field, value)

    db.commit()
    db.refresh(db_administrador)

    return db_administrador

