from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
import uuid
from datetime import datetime

class AceptarSolicitud(Base):
    __tablename__ = "aceptar_solicitud"
    id_aceptacion = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_reciclador = Column(UUID(as_uuid=True), ForeignKey("usuario_reciclador.id_reciclador"), nullable=False)
    id_solicitud = Column(UUID(as_uuid=True), ForeignKey("solicitud_materiales.id_solicitud"), nullable=False)
    fecha_aceptacion = Column(DateTime, default=datetime.utcnow)

    reciclador = relationship("UsuarioReciclador", backref="aceptaciones")
    solicitud = relationship("SolicitudMateriales", backref="aceptaciones")

class Transaccion(Base):
    __tablename__ = "transaccion" 
    id_transaccion = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_aceptacion = Column(UUID(as_uuid=True), ForeignKey("aceptar_solicitud.id_aceptacion"), nullable=False)
    cantidad_reciclada = Column(Integer, nullable=False)
    estado_transaccion = Column(String, nullable=False, default="en proceso")
    fecha_transaccion = Column(DateTime, default=datetime.utcnow)

    aceptacion = relationship("AceptarSolicitud", backref="transacciones")
