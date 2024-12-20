import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import auth_routes, chat_routes, prueba, material_routes, announcement_routes, publicacion_routes, transaction_routes

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

app.mount("/uploads", StaticFiles(directory=os.path.join(os.getcwd(), "uploads")), name="uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.get("/")
def inicio():
    return{"Hello": "World"}

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_routes.router, tags=["Autenticación"])
app.include_router(prueba.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(material_routes.router, prefix="/materiales", tags=["Materiales"])
app.include_router(announcement_routes.router, prefix="/anuncios", tags=["Anuncios"])
app.include_router(transaction_routes.router, prefix="/transacciones", tags=["Transacciones"])

#Rutas de MongoDB
app.include_router(publicacion_routes.router, prefix="/publicaciones", tags=["Publicaciones"])
app.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])
