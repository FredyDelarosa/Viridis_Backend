from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
import uuid
 
class Usuario(Base):
    __tablename__ = "usuario" 
    id_usuario = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_usuario = Column(String, nullable=False)

class UsuarioReciclador(Base):
    __tablename__ = "usuario_reciclador" 
    id_reciclador = Column(UUID(as_uuid=True), ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    usuario = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    contraseña = Column(String, nullable=False)

    usuario_base = relationship("Usuario", backref="reciclador", cascade="all, delete")

class UsuarioEmpresa(Base):
    __tablename__ = "usuario_empresa"
    id_empresa = Column(UUID(as_uuid=True), ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    nombre_empresa = Column(String, nullable=False)
    dueño_empresa = Column(String, nullable=False)
    direccion = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefono = Column(String)
    estado = Column(String, nullable=False)
    ciudad = Column(String)
    municipio = Column(String)
    contraseña = Column(String, nullable=False)
    imagen_empresa = Column(String, nullable=True)


class UsuarioAdministrador(Base):
    __tablename__ = "usuario_administrador"
    id_administrador = Column(UUID(as_uuid=True), ForeignKey("usuario.id_usuario", ondelete="CASCADE"), primary_key=True)
    usuario = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    contraseña = Column(String, nullable=False)