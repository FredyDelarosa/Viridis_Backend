from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MensajeBase(BaseModel):
    id_remitente: str  # ID del remitente
    id_destinatario: str  # ID del destinatario
    mensaje: str
    fecha_envio: datetime = datetime.utcnow()
    estado: Optional[str] = "no_leído"  # Estado del mensaje

class MensajeResponse(MensajeBase):
    id: str  # El ID del mensaje en formato de cadena

    class Config:
        orm_mode = True