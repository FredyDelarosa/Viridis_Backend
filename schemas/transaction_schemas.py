from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


# Esquema para Aceptar Solicitud
class AceptarSolicitudBase(BaseModel):
    id_reciclador: UUID
    id_solicitud: UUID

class AceptarSolicitudCreate(AceptarSolicitudBase):
    pass

class AceptarSolicitudResponse(AceptarSolicitudBase):
    id_aceptacion: UUID
    fecha_aceptacion: datetime

    class Config:
        from_attributes = True 

# Esquema para Transaccion
class TransaccionBase(BaseModel):
    id_aceptacion: UUID
    cantidad_reciclada: int

class TransaccionCreate(TransaccionBase):
    pass

class TransaccionResponse(TransaccionBase):
    id_transaccion: UUID
    estado_transaccion: str
    fecha_transaccion: datetime

    class Config:
        from_attributes = True  
        
class AcceptAndTransactPayload(BaseModel):
    id_reciclador: UUID
    id_solicitud: UUID
    cantidad_reciclada: int
