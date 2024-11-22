import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from db.database import get_db
from models.material_models import Materiales, SolicitudMateriales
from models.user_models import UsuarioEmpresa
from schemas.material_schemas import (MaterialCreate, MaterialUpdate,MaterialResponse, SolicitudMaterialResponse)
from crud.material_crud import (create_material, get_material, get_materiales, update_material, delete_material
)

router = APIRouter()

UPLOAD_FOLDER = "uploads/solicitudes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("/materiales", response_model=MaterialResponse)
def create_material_route(id_empresa: UUID, material: MaterialCreate, db: Session = Depends(get_db)):
    return create_material(db, material, id_empresa)

@router.get("/materiales/{material_id}", response_model=MaterialResponse)
def read_material(material_id: UUID, db: Session = Depends(get_db)):
    db_material = get_material(db, material_id)
    if db_material is None:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return db_material

@router.get("/materiales", response_model=list[MaterialResponse])
def read_materiales(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_materiales(db, skip=skip, limit=limit)

@router.put("/materiales/{material_id}", response_model=MaterialResponse)
def update_material_route(material_id: UUID, material: MaterialUpdate, db: Session = Depends(get_db)):
    db_material = update_material(db, material_id, material)
    if db_material is None:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return db_material

@router.delete("/materiales/{material_id}", response_model=MaterialResponse)
def delete_material_route(material_id: UUID, db: Session = Depends(get_db)):
    db_material = delete_material(db, material_id)
    if db_material is None:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return db_material

@router.post("/solicitudes", response_model=SolicitudMaterialResponse, status_code=201)
async def create_solicitud_materiales(
    id_material: str = Form(...),
    cantidad_solicitada: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verificar que el material existe
    material = db.query(Materiales).filter(Materiales.id_material == id_material).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    # Obtener la empresa asociada al material
    empresa = db.query(UsuarioEmpresa).filter(UsuarioEmpresa.id_empresa == material.id_empresa).first()
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa asociada no encontrada")

    # Guardar la imagen
    filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    image_url = f"/uploads/solicitudes/{filename}"

    # Crear la solicitud en la base de datos
    solicitud = SolicitudMateriales(
        id_material=id_material,
        cantidad_solicitada=cantidad_solicitada,
        imagen_solicitud=image_url,
        estado_solicitud="pendiente"
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    # Construir y devolver la respuesta con datos relacionados
    return {
        "id_solicitud": str(solicitud.id_solicitud),
        "cantidad_solicitada": solicitud.cantidad_solicitada,
        "fecha_solicitud": solicitud.fecha_solicitud,
        "estado_solicitud": solicitud.estado_solicitud,
        "imagen_solicitud": solicitud.imagen_solicitud,
        "nombre_material": material.nombre_material,
        "nombre_empresa": empresa.nombre_empresa
    }

@router.get("/solicitudes_materiales", response_model=list[SolicitudMaterialResponse])
def read_solicitudes_materiales(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    solicitudes = (
        db.query(
            SolicitudMateriales,
            Materiales.nombre_material,
            UsuarioEmpresa.nombre_empresa,
        )
        .join(Materiales, SolicitudMateriales.id_material == Materiales.id_material)
        .join(UsuarioEmpresa, Materiales.id_empresa == UsuarioEmpresa.id_empresa)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Convertir los resultados en la estructura esperada
    response = [
        SolicitudMaterialResponse(
            id_solicitud=solicitud[0].id_solicitud,
            nombre_material=solicitud[1],  # nombre_material
            cantidad_solicitada=solicitud[0].cantidad_solicitada,
            fecha_solicitud=solicitud[0].fecha_solicitud,
            estado_solicitud=solicitud[0].estado_solicitud,
            imagen_solicitud=solicitud[0].imagen_solicitud,
            nombre_empresa=solicitud[2],  # nombre_empresa
        )
        for solicitud in solicitudes
    ]

    return response
