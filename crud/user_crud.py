from http.client import HTTPException
from sqlalchemy.orm import Session
from auth import get_password_hash
from models.user_models import Usuario, UsuarioAdministrador, UsuarioEmpresa, UsuarioReciclador
from schemas.user_schemas import UsuarioAdministradorCreate, UsuarioEmpresaCreate, UsuarioRecicladorCreate
from uuid import UUID
import uuid
from sqlalchemy.exc import SQLAlchemyError

def create_usuario_empresa(db: Session, empresa_data: UsuarioEmpresaCreate):
    try:
        # Crear el registro en la tabla `usuario`
        usuario_base = Usuario(id_usuario=uuid.uuid4(), tipo_usuario="Empresa")
        db.add(usuario_base)
        db.commit()  # Confirmar la transacción
        db.refresh(usuario_base)  # Refrescar para obtener el objeto completo con su ID

        # Verificar que el registro en `usuario` se haya creado correctamente
        if not usuario_base.id_usuario:
            raise HTTPException(status_code=500, detail="Error al crear el usuario base.")

        # Crear el registro en la tabla `usuario_empresa`
        nueva_empresa = UsuarioEmpresa(
            id_empresa=usuario_base.id_usuario,
            nombre_empresa=empresa_data.nombre_empresa,
            dueño_empresa=empresa_data.dueño_empresa,
            direccion=empresa_data.direccion,
            email=empresa_data.email,
            telefono=empresa_data.telefono,
            estado=empresa_data.estado,
            ciudad=empresa_data.ciudad,
            municipio=empresa_data.municipio,
            contraseña=get_password_hash(empresa_data.contraseña),
            imagen_empresa=getattr(empresa_data, "imagen_empresa", None),  # Manejar campos opcionales
        )
        db.add(nueva_empresa)
        db.commit()  # Confirmar la transacción
        db.refresh(nueva_empresa)  # Refrescar el objeto para obtener el ID actualizado

        return nueva_empresa

    except SQLAlchemyError as e:
        db.rollback()  # Revertir la transacción en caso de error
        raise HTTPException(status_code=500, detail=f"Error al crear usuario empresa: {str(e)}")




def get_usuario_empresa(db: Session, empresa_id: UUID):
    return db.query(UsuarioEmpresa).filter(UsuarioEmpresa.id_empresa == empresa_id).first()

def get_usuarios_empresa(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UsuarioEmpresa).offset(skip).limit(limit).all()

def update_usuario_empresa(db: Session, empresa_id: UUID, usuario_data: UsuarioEmpresaCreate):
    db_empresa = get_usuario_empresa(db, empresa_id)
    if db_empresa:
        db_empresa.nombre_empresa = usuario_data.nombre_empresa
        db_empresa.dueño_empresa = usuario_data.dueño_empresa
        db_empresa.direccion = usuario_data.direccion
        db_empresa.email = usuario_data.email
        db_empresa.telefono = usuario_data.telefono
        db_empresa.estado = usuario_data.estado
        db_empresa.ciudad = usuario_data.ciudad
        db_empresa.municipio = usuario_data.municipio
        db_empresa.contraseña = usuario_data.contraseña
        db.commit()
        db.refresh(db_empresa)
    return db_empresa

def delete_usuario_empresa(db: Session, empresa_id: UUID):
    db_empresa = get_usuario_empresa(db, empresa_id)
    if db_empresa:
        db.delete(db_empresa)
        db.commit()
    return db_empresa

def create_usuario_reciclador(db: Session, reciclador_data: UsuarioRecicladorCreate):
    # Crear el usuario base en la tabla Usuario
    db_usuario = Usuario(id_usuario=uuid.uuid4(), tipo_usuario="Reciclador")
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    # Crear el usuario específico en la tabla Usuario_Reciclador
    db_reciclador = UsuarioReciclador(
        id_reciclador=db_usuario.id_usuario,
        usuario=reciclador_data.usuario,
        email=reciclador_data.email,
        contraseña=get_password_hash(reciclador_data.contraseña)
    )
    db.add(db_reciclador)
    db.commit()
    db.refresh(db_reciclador)
    return db_reciclador

def get_usuario_reciclador(db: Session, reciclador_id: UUID):
    return db.query(UsuarioReciclador).filter(UsuarioReciclador.id_reciclador == reciclador_id).first()

def get_usuarios_recicladores(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UsuarioReciclador).offset(skip).limit(limit).all()

def delete_usuario_reciclador(db: Session, reciclador_id: UUID):
    db_reciclador = get_usuario_reciclador(db, reciclador_id)
    if db_reciclador:
        db.delete(db_reciclador)
        db.commit()
    return db_reciclador


def create_usuario_administrador(db: Session, admin_data: UsuarioAdministradorCreate):
    # Crear el usuario base en la tabla usuario
    db_usuario = Usuario(id_usuario=uuid.uuid4(), tipo_usuario="Administrador")
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    # Crear el usuario específico en la tabla usuario_administrador
    db_administrador = UsuarioAdministrador(
        id_administrador=db_usuario.id_usuario,
        usuario=admin_data.usuario,
        email=admin_data.email,
        contraseña=get_password_hash(admin_data.contraseña)
    )
    db.add(db_administrador)
    db.commit()
    db.refresh(db_administrador)
    return db_administrador

def get_usuario_administrador(db: Session, administrador_id: UUID):
    return db.query(UsuarioAdministrador).filter(UsuarioAdministrador.id_administrador == administrador_id).first()

def get_usuarios_administradores(db: Session, skip: int = 0, limit: int = 10):
    return db.query(UsuarioAdministrador).offset(skip).limit(limit).all()

def delete_usuario_administrador(db: Session, administrador_id: UUID):
    db_administrador = get_usuario_administrador(db, administrador_id)
    if db_administrador:
        db.delete(db_administrador)
        db.commit()
    return db_administrador