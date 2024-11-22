from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from db.database import get_db
from schemas.transaction_schemas import (AceptarSolicitudCreate, AceptarSolicitudResponse, TransaccionCreate, TransaccionResponse)
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
