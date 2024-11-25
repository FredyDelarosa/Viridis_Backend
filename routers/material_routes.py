import os
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from db.database import get_db
from models.material_models import Materiales, SolicitudMateriales
from models.user_models import UsuarioEmpresa
from schemas.material_schemas import (MaterialCreate, MaterialUpdate,MaterialResponse, SolicitudMaterialResponse)
from crud.material_crud import (create_material, create_solicitud_material, get_material, get_materiales, update_material, delete_material
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

@router.get("/materialesbycompany", response_model=List[MaterialResponse])
def get_materiales_por_empresa(id_empresa: UUID, db: Session = Depends(get_db)):
    materiales = db.query(Materiales).filter(Materiales.id_empresa == id_empresa).all()
    if not materiales:
        raise HTTPException(status_code=404, detail="No se encontraron materiales para esta empresa")
    return materiales


@router.get("/materiales", response_model=list[MaterialResponse])
def read_materiales(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_materiales(db, skip=skip, limit=limit)

@router.put("/materiales/{material_id}", response_model=MaterialResponse)
def update_material_route(material_id: UUID, material: MaterialUpdate, db: Session = Depends(get_db)):
    print(f"ID recibido: {material_id}, Datos: {material}")
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
    precio: float = Form(...),
    descripcion: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Verificar que el material existe
    material = db.query(Materiales).filter(Materiales.id_material == id_material).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    # Guardar la imagen
    filename = f"{uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    image_url = f"/uploads/solicitudes/{filename}"

    # Crear la solicitud en la base de datos
    solicitud_data = {
        "id_material": id_material,
        "cantidad_solicitada": cantidad_solicitada,
        "precio": precio,
        "descripcion": descripcion,
    }
    solicitud = create_solicitud_material(db, solicitud_data, image_url)

    # Construir y devolver la respuesta
    return {
        "id_solicitud": str(solicitud.id_solicitud),
        "id_material": id_material,  # Agregado
        "cantidad_solicitada": solicitud.cantidad_solicitada,
        "precio": solicitud.precio,
        "descripcion": solicitud.descripcion,
        "fecha_solicitud": solicitud.fecha_solicitud,
        "estado_solicitud": solicitud.estado_solicitud,
        "imagen_solicitud": solicitud.imagen_solicitud,
        "nombre_material": material.nombre_material,
    }


@router.get("/solicitudes_materiales", response_model=List[SolicitudMaterialResponse])
def read_solicitudes_materiales(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        solicitudes = (
            db.query(
                SolicitudMateriales,
                Materiales.nombre_material,
                UsuarioEmpresa.nombre_empresa,
            )
            .join(Materiales, SolicitudMateriales.id_material == Materiales.id_material)
            .join(UsuarioEmpresa, Materiales.id_empresa == UsuarioEmpresa.id_empresa)
            .order_by(SolicitudMateriales.fecha_solicitud.desc())  # Ordenar por fecha descendente
            .offset(skip)
            .limit(limit)
            .all()
        )

        response = []

        for solicitud in solicitudes:
            imagen_nombre = solicitud[0].imagen_solicitud  # Obtener el valor actual

            # Depurar valor actual de imagen_solicitud
            print(f"Valor de imagen_solicitud: {imagen_nombre}")

            # Si ya contiene "uploads/solicitudes/", elimina el prefijo duplicado
            if imagen_nombre and imagen_nombre.startswith("uploads/solicitudes/"):
                imagen_nombre = imagen_nombre.replace("uploads/solicitudes/", "")

            # Construir URL completa
            imagen_url = (
                f"http://127.0.0.1:8000{imagen_nombre}" 
                if imagen_nombre else "https://via.placeholder.com/150"
            )

            # Crear el objeto de respuesta
            response.append(
                SolicitudMaterialResponse(
                    id_solicitud=solicitud[0].id_solicitud,
                    nombre_material=solicitud[1],
                    cantidad_solicitada=solicitud[0].cantidad_solicitada,
                    fecha_solicitud=solicitud[0].fecha_solicitud,
                    estado_solicitud=solicitud[0].estado_solicitud,
                    imagen_solicitud=imagen_url,  # Usar la URL corregida
                    nombre_empresa=solicitud[2],
                    id_material=str(solicitud[0].id_material),
                    descripcion=solicitud[0].descripcion or "Sin descripción",
                    precio=solicitud[0].precio,
                )
            )

        return response
    except Exception as e:
        print(f"Error al obtener solicitudes de materiales: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
    
@router.get("/solicitudes_materiales/{id}", response_model=SolicitudMaterialResponse)
def get_solicitud_material(id: str, db: Session = Depends(get_db)):
    try:
        solicitud = (
            db.query(
                SolicitudMateriales,
                Materiales.nombre_material,
                UsuarioEmpresa.nombre_empresa,
            )
            .join(Materiales, SolicitudMateriales.id_material == Materiales.id_material)
            .join(UsuarioEmpresa, Materiales.id_empresa == UsuarioEmpresa.id_empresa)
            .filter(SolicitudMateriales.id_solicitud == id)
            .first()
        )

        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")

        return SolicitudMaterialResponse(
            id_solicitud=solicitud[0].id_solicitud,
            nombre_material=solicitud[1],  # Materiales.nombre_material
            cantidad_solicitada=solicitud[0].cantidad_solicitada,
            precio=solicitud[0].precio,
            descripcion=solicitud[0].descripcion or "Sin descripción",
            fecha_solicitud=solicitud[0].fecha_solicitud,
            estado_solicitud=solicitud[0].estado_solicitud,
            imagen_solicitud=(
                f"http://127.0.0.1:8000{solicitud[0].imagen_solicitud}" 
                if solicitud[0].imagen_solicitud else "https://via.placeholder.com/150"
            ),
            nombre_empresa=solicitud[2],  # UsuarioEmpresa.nombre_empresa
            id_material=str(solicitud[0].id_material),  # Convertir UUID a cadena
        )
    except Exception as e:
        print(f"Error al obtener la solicitud: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")



@router.get("/solicitudes_empresa", response_model=list[SolicitudMaterialResponse])
def read_solicitudes_empresa(
    id_empresa: str,
    db: Session = Depends(get_db)
):
    # Filtrar las solicitudes por empresa y ordenarlas por fecha de solicitud (descendente)
    solicitudes = (
        db.query(
            SolicitudMateriales,
            Materiales.nombre_material,
            UsuarioEmpresa.nombre_empresa,
        )
        .join(Materiales, SolicitudMateriales.id_material == Materiales.id_material)
        .join(UsuarioEmpresa, Materiales.id_empresa == UsuarioEmpresa.id_empresa)
        .filter(Materiales.id_empresa == id_empresa)
        .order_by(desc(SolicitudMateriales.fecha_solicitud))  # Orden descendente
        .all()
    )

    # Convertir los resultados en la estructura esperada
    response = [
        SolicitudMaterialResponse(
            id_solicitud=str(solicitud[0].id_solicitud),
            id_material=str(solicitud[0].id_material),
            cantidad_solicitada=solicitud[0].cantidad_solicitada,
            precio=solicitud[0].precio if solicitud[0].precio is not None else 0.0,
            descripcion=solicitud[0].descripcion if solicitud[0].descripcion else "Sin descripción",
            fecha_solicitud=solicitud[0].fecha_solicitud,
            estado_solicitud=solicitud[0].estado_solicitud,
            imagen_solicitud=solicitud[0].imagen_solicitud,
            nombre_material=solicitud[1],
            nombre_empresa=solicitud[2],
        )
        for solicitud in solicitudes
    ]

    return response

@router.put("/materiales/solicitudes/{id_solicitud}", response_model=SolicitudMaterialResponse)
async def update_solicitud_material(
    id_solicitud: str,
    cantidad_solicitada: Optional[int] = Form(None),
    precio: Optional[float] = Form(None),
    descripcion: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    solicitud = db.query(SolicitudMateriales).filter_by(id_solicitud=id_solicitud).first()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    # Actualizar campos permitidos
    if cantidad_solicitada is not None:
        solicitud.cantidad_solicitada = cantidad_solicitada
    if precio is not None:
        solicitud.precio = precio
    if descripcion is not None:
        solicitud.descripcion = descripcion

    # Si se carga una nueva imagen
    if file:
        filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        solicitud.imagen_solicitud = f"/uploads/solicitudes/{filename}"

    db.commit()
    db.refresh(solicitud)

    # Construir la respuesta esperada
    return {
        "id_solicitud": str(solicitud.id_solicitud),
        "id_material": str(solicitud.id_material),  # Convertir a cadena
        "cantidad_solicitada": solicitud.cantidad_solicitada,
        "precio": solicitud.precio,
        "descripcion": solicitud.descripcion,
        "fecha_solicitud": solicitud.fecha_solicitud,
        "estado_solicitud": solicitud.estado_solicitud,
        "imagen_solicitud": solicitud.imagen_solicitud,
        "nombre_material": solicitud.material.nombre_material,  # Agregar el nombre del material
    }
    
@router.delete("/materiales/solicitudes/{id_solicitud}", status_code=204)
def delete_solicitud_material(
    id_solicitud: str,
    db: Session = Depends(get_db),
):
    solicitud = db.query(SolicitudMateriales).filter(SolicitudMateriales.id_solicitud == id_solicitud).first()

    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    db.delete(solicitud)
    db.commit()
    return {"message": "Solicitud eliminada correctamente"}


