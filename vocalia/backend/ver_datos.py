"""Muestra lo que hay guardado en la base de datos (usuarios, evaluaciones, perfiles y opiniones).

Uso (desde la carpeta backend):
    python ver_datos.py
"""
import os
import sys

# database.py vive en la carpeta frontend
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend"))

from sqlalchemy import text  # noqa: E402
from database import SessionLocal  # type: ignore


def mostrar(db, titulo, sql):
    print(f"\n=== {titulo} ===")
    filas = db.execute(text(sql)).fetchall()
    if not filas:
        print("(sin datos)")
    for fila in filas:
        print(tuple(fila))


db = SessionLocal()
try:
    mostrar(db, "USUARIOS",
            "SELECT id_usuario, nombre, correo, rol, colegio, grado, edad, sexo FROM usuarios ORDER BY id_usuario")
    mostrar(db, "EVALUACIONES",
            "SELECT id_evaluacion, id_usuario, fecha, estado, nivel_adaptativo, "
            "(respuestas_json IS NOT NULL) AS con_respuestas, (perfil_json IS NOT NULL) AS con_perfil "
            "FROM evaluaciones ORDER BY id_evaluacion")
    mostrar(db, "PERFILES",
            "SELECT id_usuario, LEFT(resumen_personalidad, 80) FROM perfiles_vocacionales ORDER BY id_perfil")
    mostrar(db, "OPINIONES",
            "SELECT id_usuario, nivel_satisfaccion, LEFT(comentarios, 60) FROM retroalimentacion ORDER BY id_feedback")
    mostrar(db, "CARRERAS CARGADAS", "SELECT COUNT(*) FROM carreras")
finally:
    db.close()