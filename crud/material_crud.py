from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from models.material_models import Materiales, SolicitudMateriales
from models.user_models import UsuarioEmpresa
from schemas.material_schemas import MaterialCreate, MaterialUpdate, SolicitudMaterialResponse

def create_material(db: Session, material_data: MaterialCreate, id_empresa: UUID):
    db_material = Materiales(
        nombre_material=material_data.nombre_material,
        cantidad=material_data.cantidad,
        id_empresa=id_empresa
    )
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

def get_material(db: Session, material_id: UUID):
    return db.query(Materiales).filter(Materiales.id_material == material_id).first()

def get_materiales(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Materiales).offset(skip).limit(limit).all()

def update_material(db: Session, material_id: UUID, material_data: MaterialUpdate):
    db_material = get_material(db, material_id)
    if db_material:
        if material_data.nombre_material is not None:
            db_material.nombre_material = material_data.nombre_material
        if material_data.cantidad is not None:
            db_material.cantidad = material_data.cantidad
        db.commit()
        db.refresh(db_material)
    return db_material

def delete_material(db: Session, material_id: UUID):
    db_material = get_material(db, material_id)
    if db_material:
        db.delete(db_material)
        db.commit()
    return db_material

def create_solicitud_material(db: Session, solicitud_data: dict, image_url: str):
    solicitud = SolicitudMateriales(
        id_material=solicitud_data["id_material"],
        cantidad_solicitada=solicitud_data["cantidad_solicitada"],
        precio=solicitud_data["precio"],  # Nuevo campo
        descripcion=solicitud_data.get("descripcion"),  # Nuevo campo
        imagen_solicitud=image_url,
        estado_solicitud="pendiente",
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud

def get_solicitudes_materiales(db: Session, skip: int = 0, limit: int = 10) -> List[SolicitudMaterialResponse]:
    # Realizar la consulta para obtener las solicitudes de materiales y detalles de la empresa
    solicitudes = db.query(SolicitudMateriales, Materiales, UsuarioEmpresa).\
        join(Materiales, SolicitudMateriales.id_material == Materiales.id_material).\
        join(UsuarioEmpresa, Materiales.id_empresa == UsuarioEmpresa.id_empresa).\
        filter(SolicitudMateriales.estado_solicitud == 'pendiente').\
        offset(skip).limit(limit).all()
    
    # Transformar los resultados en la estructura de respuesta esperada
    response = [
        SolicitudMaterialResponse(
            id_solicitud=solicitud.SolicitudMateriales.id_solicitud,
            nombre_material=solicitud.Materiales.nombre_material,
            cantidad_solicitada=solicitud.SolicitudMateriales.cantidad_solicitada,
            fecha_solicitud=solicitud.SolicitudMateriales.fecha_solicitud,
            estado_solicitud=solicitud.SolicitudMateriales.estado_solicitud,
            nombre_empresa=solicitud.UsuarioEmpresa.nombre_empresa
        ) for solicitud in solicitudes
    ]
    
    return response