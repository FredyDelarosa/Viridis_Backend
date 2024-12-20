from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.user_models import UsuarioAdministrador, UsuarioEmpresa, UsuarioReciclador
from auth import verify_password, create_access_token
from datetime import timedelta
from db.database import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = (
        db.query(UsuarioAdministrador).filter(UsuarioAdministrador.email == email).first()
        or db.query(UsuarioEmpresa).filter(UsuarioEmpresa.email == email).first()
        or db.query(UsuarioReciclador).filter(UsuarioReciclador.email == email).first()
    )

    if not user or not verify_password(password, user.contraseña):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")

    token_data = {
        "sub": str(user.id_administrador if isinstance(user, UsuarioAdministrador) else
                   user.id_empresa if isinstance(user, UsuarioEmpresa) else
                   user.id_reciclador),
        "tipo_usuario": user.__tablename__.replace("usuario_", "")
    }

    access_token = create_access_token(
        data=token_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Incluir el ID del usuario en la respuesta
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": token_data["sub"],  # Agregar el ID explícitamente
    }

