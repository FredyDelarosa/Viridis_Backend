from fastapi import APIRouter
from schemas.chat_schemas import MensajeBase, MensajeResponse
from db.database import chat_collection

router = APIRouter()

@router.post("/", response_model=MensajeResponse, status_code=201)
async def enviar_mensaje(mensaje: MensajeBase):
    mensaje_dict = mensaje.dict()
    # Insertar el mensaje en la base de datos
    result = await chat_collection.insert_one(mensaje_dict)
    mensaje_dict["id"] = str(result.inserted_id)
    return mensaje_dict

@router.get("/{id_usuario1}/{id_usuario2}", response_model=list[MensajeResponse])
async def obtener_conversacion(id_usuario1: str, id_usuario2: str):
    mensajes = []
    async for mensaje in chat_collection.find({
        "$or": [
            {"id_remitente": id_usuario1, "id_destinatario": id_usuario2},
            {"id_remitente": id_usuario2, "id_destinatario": id_usuario1}
        ]
    }).sort("fecha_envio", 1):  # Ordenar los mensajes por fecha de envío
        mensaje["id"] = str(mensaje["_id"])
        del mensaje["_id"]
        mensajes.append(mensaje)
    return mensajes
