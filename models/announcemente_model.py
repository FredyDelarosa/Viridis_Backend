from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
import uuid
from datetime import datetime

class Anuncio(Base):
    __tablename__ = "anuncio"
    id_anuncio = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_empresa = Column(UUID(as_uuid=True), ForeignKey("usuario_empresa.id_empresa", ondelete="CASCADE"), nullable=False)
    contenido_anuncio = Column(String, nullable=False)
    imagen_url = Column(String)  # Campo opcional para la URL de la imagen
    fecha_publicacion = Column(DateTime, default=datetime.utcnow)

    empresa = relationship("UsuarioEmpresa", backref="anuncios")
