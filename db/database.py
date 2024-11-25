from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from motor.motor_asyncio import AsyncIOMotorClient

SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://postgress1@localhost/viridis_prueba?client_encoding=utf8'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

#Conexión a MongoDB Atlas
MONGO_DB_URL = "mongodb+srv://233317:Tux2211call@cluster0.c29vb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(MONGO_DB_URL)
mongo_db = client["viridis_prueba"]

publicaciones_collection = mongo_db["publicaciones"]
chat_collection = mongo_db["chat"]

SECRET_KEY = "Uxp_kw4wwka81PWP27LTukZqnY6OFTY5PwRcDvuyIYM"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 80000

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Conexión a la base de datos realizada correctamente.")
except OperationalError:
    print("Error: No se pudo conectar a la base de datos.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
