from sqlalchemy import Column, Float, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base
import uuid

class Materiales(Base):
    __tablename__ = "materiales" 
    id_material = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_material = Column(String, nullable=False)
    cantidad = Column(Integer, nullable=False)
    id_empresa = Column(UUID(as_uuid=True), ForeignKey("usuario_empresa.id_empresa", ondelete="CASCADE"), nullable=False)

    empresa = relationship("UsuarioEmpresa", backref="materiales")
    
class SolicitudMateriales(Base):
    __tablename__ = "solicitud_materiales"
    
    id_solicitud = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_material = Column(UUID(as_uuid=True), ForeignKey("materiales.id_material"), nullable=False)
    cantidad_solicitada = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)  # Nuevo campo
    descripcion = Column(String, nullable=True)  # Nuevo campo
    fecha_solicitud = Column(DateTime, default=datetime.utcnow)
    estado_solicitud = Column(String, default="pendiente")
    imagen_solicitud = Column(String, nullable=True)  # Campo para la ruta de la imagen
    
    # Relación con Materiales
    material = relationship("Materiales", backref="solicitudes")
