from sqlalchemy.orm import Session
from uuid import UUID
from models.transaction_models import AceptarSolicitud, Transaccion
from schemas.transaction_schemas import AceptarSolicitudCreate, TransaccionCreate

def create_aceptar_solicitud(db: Session, aceptacion_data: AceptarSolicitudCreate):
    db_aceptacion = AceptarSolicitud(
        id_reciclador=aceptacion_data.id_reciclador,
        id_solicitud=aceptacion_data.id_solicitud
    )
    db.add(db_aceptacion)
    db.commit()
    db.refresh(db_aceptacion)
    return db_aceptacion

def get_aceptacion(db: Session, aceptacion_id: UUID):
    return db.query(AceptarSolicitud).filter(AceptarSolicitud.id_aceptacion == aceptacion_id).first()

def create_transaccion(db: Session, transaccion_data: TransaccionCreate):
    db_transaccion = Transaccion(
        id_aceptacion=transaccion_data.id_aceptacion,
        cantidad_reciclada=transaccion_data.cantidad_reciclada,
        estado_transaccion="en proceso"
    )
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

def get_transaccion(db: Session, transaccion_id: UUID):
    return db.query(Transaccion).filter(Transaccion.id_transaccion == transaccion_id).first()
