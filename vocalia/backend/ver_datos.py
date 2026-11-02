from sqlalchemy import text
from database import SessionLocal

db = SessionLocal()


def mostrar(titulo, sql):
    print(f"\n=== {titulo} ===")
    for fila in db.execute(text(sql)).fetchall():
        print(tuple(fila))


mostrar("USUARIOS", "SELECT id_usuario, nombre, correo, colegio, grado FROM usuarios ORDER BY id_usuario")
mostrar("EVALUACIONES", "SELECT id_evaluacion, id_usuario, fecha, estado FROM evaluaciones ORDER BY id_evaluacion")
mostrar("RESPUESTAS", "SELECT id_evaluacion, id_pregunta, valor FROM respuestas ORDER BY id_evaluacion, id_pregunta")
mostrar("PERFILES", "SELECT id_usuario, LEFT(resumen_personalidad, 80) FROM perfiles_vocacionales ORDER BY 1")