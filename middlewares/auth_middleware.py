from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from db.database import SECRET_KEY, ALGORITHM, get_db
from sqlalchemy.orm import Session
from models.user_models import UsuarioAdministrador, UsuarioEmpresa, UsuarioReciclador


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        tipo_usuario: str = payload.get("tipo_usuario")
        if user_id is None or tipo_usuario is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    # Buscar el usuario en la base de datos según su tipo
    if tipo_usuario == "administrador":
        user = db.query(UsuarioAdministrador).filter(UsuarioAdministrador.id_administrador == user_id).first()
    elif tipo_usuario == "empresa":
        user = db.query(UsuarioEmpresa).filter(UsuarioEmpresa.id_empresa == user_id).first()
    elif tipo_usuario == "reciclador":
        user = db.query(UsuarioReciclador).filter(UsuarioReciclador.id_reciclador == user_id).first()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")

    # Añadir tipo_usuario al usuario autenticado
    user.tipo_usuario = tipo_usuario
    return user
