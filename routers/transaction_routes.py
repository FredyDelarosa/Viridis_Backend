from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from db.database import get_db
from models.material_models import SolicitudMateriales
from models.transaction_models import AceptarSolicitud, Transaccion
from models.user_models import UsuarioReciclador
from schemas.transaction_schemas import (AceptarSolicitudCreate, AceptarSolicitudResponse, TransaccionCreate, TransaccionResponse, AcceptAndTransactPayload)
from crud.transaction_crud import (create_aceptar_solicitud, get_aceptacion, create_transaccion, get_transaccion)

router = APIRouter()

# Ruta para que un reciclador acepte una solicitud
@router.post("/aceptaciones", response_model=AceptarSolicitudResponse)
def accept_solicitud(aceptacion: AceptarSolicitudCreate, db: Session = Depends(get_db)):
    return create_aceptar_solicitud(db, aceptacion)

# Ruta para leer una aceptación específica
@router.get("/aceptaciones/{aceptacion_id}", response_model=AceptarSolicitudResponse)
def read_aceptacion(aceptacion_id: UUID, db: Session = Depends(get_db)):
    db_aceptacion = get_aceptacion(db, aceptacion_id)
    if db_aceptacion is None:
        raise HTTPException(status_code=404, detail="Aceptación no encontrada")
    return db_aceptacion

# Ruta para crear una transacción basada en una aceptación de solicitud
@router.post("/transacciones", response_model=TransaccionResponse)
def create_transaction(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    return create_transaccion(db, transaccion)

# Ruta para leer una transacción específica
@router.get("/transacciones/{transaccion_id}", response_model=TransaccionResponse)
def read_transaction(transaccion_id: UUID, db: Session = Depends(get_db)):
    db_transaccion = get_transaccion(db, transaccion_id)
    if db_transaccion is None:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return db_transaccion

@router.post("/aceptar_y_transaccionar", response_model=TransaccionResponse)
def accept_and_transact(
    payload: AcceptAndTransactPayload,  # Recibe los datos como JSON
    db: Session = Depends(get_db)
):
    print(f"Datos recibidos en el servidor: {payload}")

    id_reciclador = payload.id_reciclador
    id_solicitud = payload.id_solicitud
    cantidad_reciclada = payload.cantidad_reciclada

    # Validar existencia en la base de datos
    solicitud = db.query(SolicitudMateriales).filter(SolicitudMateriales.id_solicitud == id_solicitud).first()
    if not solicitud:
        raise HTTPException(status_code=422, detail="Solicitud no encontrada.")

    reciclador = db.query(UsuarioReciclador).filter(UsuarioReciclador.id_reciclador == id_reciclador).first()
    if not reciclador:
        raise HTTPException(status_code=422, detail="Reciclador no encontrado.")

    # Registrar aceptación y transacción
    try:
        # Aceptación
        db_aceptacion = AceptarSolicitud(
            id_reciclador=id_reciclador,
            id_solicitud=id_solicitud
        )
        db.add(db_aceptacion)
        db.commit()
        db.refresh(db_aceptacion)

        # Transacción
        db_transaccion = Transaccion(
            id_aceptacion=db_aceptacion.id_aceptacion,
            cantidad_reciclada=cantidad_reciclada,
            estado_transaccion="en proceso"
        )
        db.add(db_transaccion)
        db.commit()
        db.refresh(db_transaccion)

        return db_transaccion
    except Exception as e:
        print(f"Error al procesar la solicitud: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/reciclador/{id_reciclador}", response_model=List[TransaccionResponse])
def get_transactions_by_user(
    id_reciclador: UUID,
    db: Session = Depends(get_db)
):
    # Buscar transacciones relacionadas con el reciclador
    aceptaciones = db.query(AceptarSolicitud).filter(AceptarSolicitud.id_reciclador == id_reciclador).all()
    if not aceptaciones:
        raise HTTPException(status_code=404, detail="No se encontraron transacciones para este reciclador.")

    # Extraer transacciones asociadas a las aceptaciones
    transacciones = db.query(Transaccion).filter(
        Transaccion.id_aceptacion.in_([aceptacion.id_aceptacion for aceptacion in aceptaciones])
    ).all()

    return transacciones
