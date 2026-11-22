import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
url = os.getenv("DATABASE_URL")

try:
    conexion = psycopg2.connect(url)
    print("¡Conexión exitosa a la base de datos de Supabase!")
    conexion.close()
except Exception as e:
    print(f"Error al conectar: {e}")