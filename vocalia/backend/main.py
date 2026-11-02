import os
import json
import time
import hashlib
import secrets
import threading
from collections import Counter
from contextlib import asynccontextmanager
from typing import Dict, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

from .database import get_db, engine
import cuestionario as cq

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "").strip()
GEMINI_API_VERSION = os.getenv("GEMINI_API_VERSION", "v1beta").strip()
ORIGENES = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ADMIN_EMAILS = {e.strip().lower() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()}
MODELO_OK = None  # último modelo de Gemini que respondió bien
PK_CARRERA = "id_carrera"
BASE_LISTA = threading.Event()


def esperar_base():
    """Las consultas esperan (hasta 20 s) a que termine la preparación de la base al arrancar."""
    BASE_LISTA.wait(20)


# ======================= Base de datos: columnas, tablas y carreras de la UCV =======================
def _ejecutar(sql, params=None):
    """Ejecuta una sentencia y devuelve la lista de filas (vacía si no devuelve filas)."""
    with engine.begin() as con:
        r = con.execute(text(sql), params or {})
        return r.fetchall() if r.returns_rows else []


def sembrar_ucv():
    """Deja en la base solo las 23 carreras oficiales de la UCV sede Chiclayo (sin duplicar)."""
    try:
        with engine.begin() as con:
            sel = text("SELECT id_institucion FROM instituciones_educativas "
                       "WHERE nombre ILIKE '%Vallejo%' ORDER BY id_institucion LIMIT 1")
            fila = con.execute(sel).fetchone()
            if not fila:
                con.execute(text("""
                    INSERT INTO instituciones_educativas (id_institucion, nombre)
                    SELECT COALESCE(MAX(id_institucion), 0) + 1, :n FROM instituciones_educativas
                """), {"n": cq.UCV_NOMBRE})
                fila = con.execute(sel).fetchone()
            inst = fila[0]
        try:
            _ejecutar("SELECT setval(pg_get_serial_sequence('instituciones_educativas', 'id_institucion'), "
                      "(SELECT MAX(id_institucion) FROM instituciones_educativas))")
        except Exception:
            pass

        oficiales = {n.lower() for n, _, _ in cq.CARRERAS_UCV}
        filas = _ejecutar(f"SELECT {PK_CARRERA} AS id, nombre FROM carreras WHERE id_institucion = :i",
                          {"i": inst})
        for f in filas:  # quita carreras de la UCV que no están en la lista oficial
            if (f.nombre or "").strip().lower() not in oficiales:
                try:
                    _ejecutar(f"DELETE FROM carreras WHERE {PK_CARRERA} = :id", {"id": f.id})
                except Exception as e:
                    print("No se pudo quitar", f.nombre, "->", str(e)[:100])
        existentes = {(f.nombre or "").strip().lower()
                      for f in _ejecutar("SELECT nombre FROM carreras WHERE id_institucion = :i", {"i": inst})}

        for nombre, facultad, _area in cq.CARRERAS_UCV:
            area_conoc = facultad.replace("Facultad de ", "")
            if nombre.lower() in existentes:
                _ejecutar("UPDATE carreras SET facultad = :f, tipo = COALESCE(tipo, 'Pregrado') "
                          "WHERE id_institucion = :i AND LOWER(nombre) = LOWER(:n)",
                          {"f": facultad, "i": inst, "n": nombre})
            else:
                p = {"n": nombre, "a": area_conoc, "i": inst, "f": facultad}
                try:
                    _ejecutar("INSERT INTO carreras (nombre, area_conocimiento, id_institucion, facultad, tipo) "
                              "VALUES (:n, :a, :i, :f, 'Pregrado')", p)
                except Exception:
                    try:
                        _ejecutar(f"INSERT INTO carreras ({PK_CARRERA}, nombre, area_conocimiento, id_institucion, facultad, tipo) "
                                  f"VALUES ((SELECT COALESCE(MAX({PK_CARRERA}), 0) + 1 FROM carreras), :n, :a, :i, :f, 'Pregrado')", p)
                    except Exception as e:
                        print("No se pudo insertar", nombre, "->", str(e)[:120])
        for nombre, url in cq.MALLAS_URL.items():
            if url:
                _ejecutar("UPDATE carreras SET malla_url = :u WHERE id_institucion = :i "
                          "AND LOWER(nombre) = LOWER(:n) AND (malla_url IS NULL OR malla_url = '')",
                          {"u": url, "i": inst, "n": nombre})
        total = _ejecutar("SELECT COUNT(*) FROM carreras WHERE id_institucion = :i", {"i": inst})[0][0]
        print(f"UCV Chiclayo lista: {total} carreras en la base (oficiales: {len(oficiales)}).")
    except Exception as e:
        print("No se pudo preparar las carreras de la UCV:", str(e)[:200])


def preparar_base():
    """Agrega (si faltan) columnas y tablas nuevas y deja lista la oferta de la UCV."""
    global PK_CARRERA
    try:
        sentencias = [
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS edad INTEGER",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS sexo TEXT",
            "ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS respuestas_json TEXT",
            "ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS perfil_json TEXT",
            "ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS nivel_adaptativo INTEGER DEFAULT 1",
            "ALTER TABLE carreras ADD COLUMN IF NOT EXISTS facultad TEXT",
            "ALTER TABLE carreras ADD COLUMN IF NOT EXISTS tipo TEXT",
            "ALTER TABLE carreras ADD COLUMN IF NOT EXISTS alcance TEXT",
            "ALTER TABLE carreras ADD COLUMN IF NOT EXISTS malla TEXT",
            "ALTER TABLE carreras ADD COLUMN IF NOT EXISTS malla_url TEXT",
            "ALTER TABLE carreras ADD COLUMN IF NOT EXISTS demanda_laboral TEXT",
            "ALTER TABLE carreras ADD COLUMN IF NOT EXISTS salario_promedio NUMERIC",
            "ALTER TABLE carreras ADD COLUMN IF NOT EXISTS sectores_clave TEXT",
            """CREATE TABLE IF NOT EXISTS retroalimentacion (
                   id_feedback SERIAL PRIMARY KEY, id_usuario INTEGER,
                   nivel_satisfaccion INTEGER, comentarios TEXT, fecha TIMESTAMP DEFAULT NOW())""",
        ]
        for s in sentencias:
            try:
                _ejecutar(s)
            except Exception as e:
                print("Aviso preparando la base:", str(e)[:150])
        try:
            filas_pk = _ejecutar("""
                SELECT a.attname FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = 'carreras'::regclass AND i.indisprimary
            """)
            if filas_pk and str(filas_pk[0][0]).isidentifier():
                PK_CARRERA = str(filas_pk[0][0])
        except Exception as e:
            print("No se pudo detectar la clave de carreras:", str(e)[:150])
        sembrar_ucv()
    finally:
        BASE_LISTA.set()


@asynccontextmanager
async def lifespan(app_):
    threading.Thread(target=preparar_base, daemon=True).start()
    yield


# ======================= Gemini =======================
def _modelos_disponibles(client) -> list:
    nombres = []
    try:
        for m in client.models.list():
            acciones = getattr(m, "supported_actions", None) or []
            if acciones and "generateContent" not in acciones:
                continue
            n = m.name.replace("models/", "")
            if "flash" in n and not any(
                x in n for x in ("image", "tts", "live", "audio", "embedding", "thinking")
            ):
                nombres.append(n)
    except Exception:
        pass
    nombres = sorted(nombres, reverse=True)
    return sorted(nombres, key=lambda n: "lite" in n)


def consultar_gemini(prompt: str) -> dict:
    global MODELO_OK
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
        http_options=types.HttpOptions(api_version=GEMINI_API_VERSION, timeout=30_000),
    )
    candidatos = []
    for m in [MODELO_OK, GEMINI_MODEL, "gemini-flash-latest"] + _modelos_disponibles(client):
        if m and m not in candidatos:
            candidatos.append(m)
    candidatos = candidatos[:2]

    errores = []
    for modelo in candidatos:
        for intento in range(2):
            try:
                resp = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json", temperature=0.4),
                )
                perfil = json.loads(resp.text)
                MODELO_OK = modelo
                return perfil
            except Exception as e:
                msg = str(e)
                if intento == 0 and ("503" in msg or "UNAVAILABLE" in msg or "429" in msg):
                    time.sleep(2)
                    continue
                errores.append(f"{modelo}: {msg[:110]}")
                break
    raise RuntimeError(" | ".join(errores))


# ======================= App =======================
app = FastAPI(
    title="Vocacional IA API",
    description="Orientación vocacional basada en las carreras de la UCV sede Chiclayo",
    version="4.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=ORIGENES, allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(Exception)
async def error_general(request, exc):
    return JSONResponse(status_code=500,
                        content={"detail": f"{type(exc).__name__}: {str(exc)[:500]}"})


# ======================= Utilidades =======================
def hashear(password: str) -> str:
    sal = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), sal.encode(), 200_000).hex()
    return f"{sal}${h}"


def verificar(password: str, guardado: str) -> bool:
    if "$" not in guardado:  # cuentas antiguas con contraseña en texto plano
        return secrets.compare_digest(password, guardado)
    sal, h = guardado.split("$", 1)
    calc = hashlib.pbkdf2_hmac("sha256", password.encode(), sal.encode(), 200_000).hex()
    return secrets.compare_digest(calc, h)


def rol_de(correo, rol_db) -> str:
    if (correo or "").lower() in ADMIN_EMAILS or (rol_db or "").lower().startswith("admin"):
        return "Administrador"
    return "Estudiante"


def leer_json(v):
    """Lee un JSON venga como texto o ya convertido (dict/list), según el tipo de la columna en la base."""
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return v
    return json.loads(v)


def exigir_admin(db: Session, id_usuario: int):
    u = db.execute(text("SELECT correo, rol FROM usuarios WHERE id_usuario = :i"),
                   {"i": id_usuario}).fetchone()
    if not u or rol_de(u.correo, u.rol) != "Administrador":
        raise HTTPException(403, "Solo el administrador puede hacer esto")


def listar_carreras_db(db: Session) -> list:
    """Solo carreras de la UCV (la oferta del sistema)."""
    esperar_base()
    filas = db.execute(text(f"""
        SELECT c.{PK_CARRERA} AS id, c.nombre, c.area_conocimiento, c.facultad, c.tipo, c.alcance,
               c.malla, c.malla_url, c.demanda_laboral, c.salario_promedio, c.sectores_clave,
               i.nombre AS universidad
        FROM carreras c
        JOIN instituciones_educativas i ON c.id_institucion = i.id_institucion
        WHERE i.nombre ILIKE '%Vallejo%'
    """)).fetchall()
    out = []
    for f in filas:
        area = cq.area_de_carrera(f.nombre, f.area_conocimiento or "")
        url = (f.malla_url or "").strip()
        out.append({
            "id": f.id, "nombre": f.nombre, "universidad": f.universidad or "",
            "facultad": f.facultad or cq.facultad_de(f.nombre) or "Otras carreras",
            "area_conocimiento": f.area_conocimiento, "tipo": f.tipo, "alcance": f.alcance,
            "malla": (f.malla or "").strip(),
            "malla_url": url,
            "url_malla": url or cq.URL_CARRERAS_UCV,
            "malla_directa": bool(url),
            "demanda_laboral": f.demanda_laboral,
            "salario_promedio": float(f.salario_promedio) if f.salario_promedio is not None else None,
            "sectores_clave": f.sectores_clave,
            "area_clave": area,
            "area_nombre": cq.AREAS[area]["nombre"] if area else None,
            "icono": cq.AREAS[area]["icono"] if area else "🎓",
        })
    out.sort(key=lambda c: (cq.ORDEN_CARRERA.get(c["nombre"].strip().lower(), 999), c["nombre"]))
    return out


def armar_resumen(evaluaciones, opiniones):
    """Cifras generales para el panel de reportes del administrador."""
    areas = Counter(e["area_principal"] for e in evaluaciones if e["area_principal"])
    carreras = Counter(e["carrera_principal"] for e in evaluaciones if e["carrera_principal"])
    notas = [o["nivel_satisfaccion"] for o in opiniones if o["nivel_satisfaccion"]]
    return {
        "estudiantes": len({e["id_usuario"] for e in evaluaciones}),
        "evaluaciones": len(evaluaciones),
        "con_ia": sum(1 for e in evaluaciones if e["modo"] == "ia"),
        "satisfaccion": round(sum(notas) / len(notas), 1) if notas else None,
        "opiniones": len(notas),
        "areas": dict(areas.most_common()),
        "carreras": dict(carreras.most_common(10)),
    }


# ======================= Modelos de entrada =======================
class IngresoIn(BaseModel):
    nombre: str
    edad: Optional[int] = None
    sexo: Optional[str] = None
    colegio: str
    grado: str


class LoginIn(BaseModel):
    correo: str
    contrasena: str


class AdminRegistroIn(BaseModel):
    nombre: str
    correo: str
    contrasena: str


class AdaptativasIn(BaseModel):
    respuestas: Dict[str, int]


class EvaluacionIn(BaseModel):
    id_usuario: int
    respuestas: Dict[str, int]
    nivel_adaptativo: int = 1


class CarreraIn(BaseModel):
    id_admin: int
    nombre: str
    facultad: Optional[str] = None
    area_conocimiento: Optional[str] = None
    tipo: Optional[str] = None
    alcance: Optional[str] = None
    malla: Optional[str] = None
    malla_url: Optional[str] = None
    demanda_laboral: Optional[str] = None
    salario_promedio: Optional[float] = None
    sectores_clave: Optional[str] = None


class FeedbackIn(BaseModel):
    id_usuario: int
    nivel_satisfaccion: int
    comentarios: Optional[str] = ""


# ======================= Endpoints =======================
@app.get("/")
def estado():
    return {"status": "OK", "message": "API de Vocacional IA (UCV Chiclayo) funcionando", "version": "4.0.0"}


@app.post("/ingresar")
def ingresar(datos: IngresoIn, db: Session = Depends(get_db)):
    """Ingreso del estudiante sin cuenta ni contraseña: solo sus datos básicos."""
    esperar_base()
    nombre = " ".join(datos.nombre.split())
    colegio = " ".join(datos.colegio.split())
    if len(nombre) < 3:
        raise HTTPException(400, "Escribe tu nombre completo")
    if not colegio:
        raise HTTPException(400, "Escribe el nombre de tu colegio")
    u = db.execute(text("""
        SELECT id_usuario FROM usuarios
        WHERE LOWER(nombre) = LOWER(:n) AND LOWER(colegio) = LOWER(:c)
          AND LOWER(COALESCE(rol, 'Estudiante')) NOT LIKE 'admin%'
        ORDER BY id_usuario LIMIT 1
    """), {"n": nombre, "c": colegio}).fetchone()
    if u:
        try:
            db.execute(text("UPDATE usuarios SET edad = :e, sexo = :s, grado = :g WHERE id_usuario = :id"),
                       {"e": datos.edad, "s": datos.sexo, "g": datos.grado, "id": u.id_usuario})
            db.commit()
        except Exception:
            db.rollback()
        return {"id_usuario": u.id_usuario, "nombre": nombre, "rol": "Estudiante"}

    params = {"n": nombre, "c": f"est-{secrets.token_hex(6)}@estudiante.local",
              "p": hashear(secrets.token_hex(16)), "col": colegio, "g": datos.grado,
              "e": datos.edad, "s": datos.sexo}
    try:
        fila = db.execute(text("""
            INSERT INTO usuarios (nombre, correo, contrasena, rol, colegio, grado, edad, sexo)
            VALUES (:n, :c, :p, 'Estudiante', :col, :g, :e, :s) RETURNING id_usuario
        """), params).fetchone()
    except Exception:
        db.rollback()
        fila = db.execute(text("""
            INSERT INTO usuarios (nombre, correo, contrasena, rol, colegio, grado)
            VALUES (:n, :c, :p, 'Estudiante', :col, :g) RETURNING id_usuario
        """), params).fetchone()
    db.commit()
    return {"id_usuario": fila.id_usuario, "nombre": nombre, "rol": "Estudiante"}


@app.post("/admin/registro")
def registro_admin(datos: AdminRegistroIn, db: Session = Depends(get_db)):
    """Solo los correos listados en ADMIN_EMAILS (.env) pueden crear cuenta de administrador."""
    correo = datos.correo.strip().lower()
    if correo not in ADMIN_EMAILS:
        raise HTTPException(403, "Ese correo no está autorizado. Agrégalo en ADMIN_EMAILS del archivo .env y reinicia el backend.")
    if len(datos.contrasena) < 6:
        raise HTTPException(400, "La contraseña debe tener al menos 6 caracteres")
    if db.execute(text("SELECT 1 FROM usuarios WHERE LOWER(correo) = :c"), {"c": correo}).fetchone():
        raise HTTPException(409, "Ya existe una cuenta con ese correo. Inicia sesión.")
    fila = db.execute(text("""
        INSERT INTO usuarios (nombre, correo, contrasena, rol, colegio, grado)
        VALUES (:n, :c, :p, 'Administrador', 'UCV', '-') RETURNING id_usuario
    """), {"n": datos.nombre.strip() or "Administrador", "c": correo, "p": hashear(datos.contrasena)}).fetchone()
    db.commit()
    return {"id_usuario": fila.id_usuario, "nombre": datos.nombre.strip(), "rol": "Administrador"}


@app.post("/login")
def login(datos: LoginIn, db: Session = Depends(get_db)):
    correo = datos.correo.strip().lower()
    u = db.execute(text("""
        SELECT id_usuario, nombre, correo, rol, contrasena FROM usuarios WHERE LOWER(correo) = :c
    """), {"c": correo}).fetchone()
    if not u or not verificar(datos.contrasena, u.contrasena):
        raise HTTPException(401, "Correo o contraseña incorrectos")
    return {"id_usuario": u.id_usuario, "nombre": u.nombre, "rol": rol_de(u.correo, u.rol)}


@app.get("/cuestionario")
def cuestionario():
    return cq.cuestionario_base()


@app.post("/cuestionario/adaptativas")
def adaptativas(datos: AdaptativasIn):
    preguntas = cq.preguntas_adaptativas(datos.respuestas)
    return {"preguntas": preguntas, "areas": sorted({p["area"] for p in preguntas})}


@app.post("/evaluaciones")
def guardar_evaluacion(datos: EvaluacionIn, db: Session = Depends(get_db)):
    esperar_base()
    if len(datos.respuestas) < 20:
        raise HTTPException(400, "Responde todos los temas antes de finalizar")
    ev = db.execute(text("""
        INSERT INTO evaluaciones (id_usuario, fecha, estado, respuestas_json, nivel_adaptativo)
        VALUES (:u, NOW(), 'Finalizado', :r, :n) RETURNING id_evaluacion
    """), {"u": datos.id_usuario, "r": json.dumps(datos.respuestas), "n": datos.nivel_adaptativo}).fetchone()
    db.commit()
    return {"id_evaluacion": ev.id_evaluacion}


@app.post("/generar-perfil/{id_usuario}")
def generar_perfil(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.execute(text("SELECT nombre, colegio, grado, edad FROM usuarios WHERE id_usuario = :id"),
                         {"id": id_usuario}).fetchone()
    if not usuario:
        raise HTTPException(404, f"Usuario {id_usuario} no existe")
    ev = db.execute(text("""
        SELECT id_evaluacion, respuestas_json, nivel_adaptativo FROM evaluaciones
        WHERE id_usuario = :id AND respuestas_json IS NOT NULL
        ORDER BY id_evaluacion DESC LIMIT 1
    """), {"id": id_usuario}).fetchone()
    if not ev:
        raise HTTPException(400, "Este usuario aún no completó la evaluación")

    resp = leer_json(ev.respuestas_json)
    nivel = ev.nivel_adaptativo or 1
    carreras = listar_carreras_db(db)
    if not carreras:
        raise HTTPException(503, "No hay carreras de la UCV cargadas. Revisa la terminal del backend.")

    try:
        prompt = cq.construir_prompt(
            {"nombre": usuario.nombre, "colegio": usuario.colegio, "grado": usuario.grado,
             "edad": usuario.edad}, resp, carreras)
        validas = {c["nombre"].strip().lower() for c in carreras}
        parcial = cq.normalizar_ia(consultar_gemini(prompt), validas)
        modo = "ia"
    except Exception as e:
        print("Gemini falló, usando respaldo:", str(e)[:300])
        parcial = cq.perfil_respaldo(resp, carreras)
        modo = "respaldo"

    perfil = cq.completar_perfil(parcial, resp, nivel, modo)
    mercado = {c["nombre"].strip().lower(): c for c in carreras}
    for c in perfil["carreras"]:
        m = mercado.get(c["nombre"].strip().lower())
        if m:
            c.update({"nombre": m["nombre"], "universidad": m["universidad"], "facultad": m["facultad"],
                      "demanda_laboral": m["demanda_laboral"], "salario_promedio": m["salario_promedio"],
                      "sectores_clave": m["sectores_clave"], "url_malla": m["url_malla"],
                      "malla_directa": m["malla_directa"]})

    db.execute(text("UPDATE evaluaciones SET perfil_json = :p WHERE id_evaluacion = :e"),
               {"p": json.dumps(perfil, ensure_ascii=False), "e": ev.id_evaluacion})
    db.commit()
    try:  # compatibilidad con la tabla original
        db.execute(text("INSERT INTO perfiles_vocacionales (id_usuario, resumen_personalidad) VALUES (:u, :r)"),
                   {"u": id_usuario, "r": json.dumps(perfil, ensure_ascii=False)})
        db.commit()
    except Exception:
        db.rollback()
    return {"estudiante": usuario.nombre, "perfil": perfil}


@app.get("/perfil/{id_usuario}")
def ultimo_perfil(id_usuario: int, db: Session = Depends(get_db)):
    f = db.execute(text("""
        SELECT perfil_json FROM evaluaciones
        WHERE id_usuario = :u AND perfil_json IS NOT NULL ORDER BY id_evaluacion DESC LIMIT 1
    """), {"u": id_usuario}).fetchone()
    if not f:
        raise HTTPException(404, "Aún no hay perfil generado")
    return {"perfil": leer_json(f.perfil_json)}


@app.get("/historial/{id_usuario}")
def historial(id_usuario: int, db: Session = Depends(get_db)):
    filas = db.execute(text("""
        SELECT id_evaluacion, fecha, perfil_json FROM evaluaciones
        WHERE id_usuario = :u AND perfil_json IS NOT NULL ORDER BY id_evaluacion DESC LIMIT 20
    """), {"u": id_usuario}).fetchall()
    return [{"id_evaluacion": f.id_evaluacion, "fecha": f.fecha.isoformat() if f.fecha else "",
             "perfil": leer_json(f.perfil_json)} for f in filas]


@app.get("/carreras")
def carreras(db: Session = Depends(get_db)):
    return listar_carreras_db(db)


@app.put("/admin/carreras/{id_carrera}")
def actualizar_carrera(id_carrera: int, datos: CarreraIn, db: Session = Depends(get_db)):
    exigir_admin(db, datos.id_admin)
    r = db.execute(text(f"""
        UPDATE carreras SET nombre = :n, facultad = :fa, area_conocimiento = :a, tipo = :t, alcance = :al,
               malla = :m, malla_url = :mu, demanda_laboral = :d, salario_promedio = :s, sectores_clave = :sc
        WHERE {PK_CARRERA} = :id
    """), {"n": datos.nombre.strip(), "fa": datos.facultad, "a": datos.area_conocimiento, "t": datos.tipo,
           "al": datos.alcance, "m": datos.malla, "mu": (datos.malla_url or "").strip() or None,
           "d": datos.demanda_laboral, "s": datos.salario_promedio, "sc": datos.sectores_clave,
           "id": id_carrera})
    db.commit()
    if r.rowcount == 0:
        raise HTTPException(404, "Carrera no encontrada")
    return {"ok": True}


@app.post("/retroalimentacion")
def retroalimentacion(datos: FeedbackIn, db: Session = Depends(get_db)):
    db.execute(text("""
        INSERT INTO retroalimentacion (id_usuario, nivel_satisfaccion, comentarios)
        VALUES (:u, :n, :c)
    """), {"u": datos.id_usuario, "n": max(1, min(5, datos.nivel_satisfaccion)),
           "c": (datos.comentarios or "")[:1000]})
    db.commit()
    return {"ok": True}


@app.get("/admin/reportes")
def admin_reportes(id_admin: int, db: Session = Depends(get_db)):
    """Panel del administrador: resumen general, evaluaciones realizadas y opiniones."""
    exigir_admin(db, id_admin)
    filas = db.execute(text("""
        SELECT e.id_evaluacion, e.id_usuario, e.fecha, e.perfil_json,
               u.nombre, u.colegio, u.grado, u.edad, u.sexo
        FROM evaluaciones e JOIN usuarios u ON u.id_usuario = e.id_usuario
        WHERE e.perfil_json IS NOT NULL
        ORDER BY e.id_evaluacion DESC LIMIT 500
    """)).fetchall()
    evaluaciones = []
    for f in filas:
        p = leer_json(f.perfil_json) or {}
        areas = p.get("areas") or []
        carreras_p = p.get("carreras") or []
        evaluaciones.append({
            "id_evaluacion": f.id_evaluacion, "id_usuario": f.id_usuario,
            "nombre": f.nombre, "colegio": f.colegio, "grado": f.grado, "edad": f.edad, "sexo": f.sexo,
            "fecha": f.fecha.isoformat() if f.fecha else "",
            "area_principal": areas[0]["nombre"] if areas else None,
            "carrera_principal": carreras_p[0]["nombre"] if carreras_p else None,
            "afinidad": carreras_p[0].get("afinidad") if carreras_p else None,
            "modo": p.get("modo"),
        })
    ops = db.execute(text("""
        SELECT r.nivel_satisfaccion, r.comentarios, r.fecha, u.nombre
        FROM retroalimentacion r LEFT JOIN usuarios u ON u.id_usuario = r.id_usuario
        ORDER BY r.id_feedback DESC LIMIT 100
    """)).fetchall()
    opiniones = [{"nivel_satisfaccion": o.nivel_satisfaccion, "comentarios": o.comentarios,
                  "fecha": o.fecha.isoformat() if o.fecha else "", "nombre": o.nombre} for o in ops]
    return {"resumen": armar_resumen(evaluaciones, opiniones), "evaluaciones": evaluaciones, "opiniones": opiniones}


@app.get("/admin/reportes/{id_evaluacion}")
def admin_reporte(id_evaluacion: int, id_admin: int, db: Session = Depends(get_db)):
    """Perfil completo de una evaluación, para ver o descargar su reporte."""
    exigir_admin(db, id_admin)
    f = db.execute(text("""
        SELECT e.perfil_json, u.nombre FROM evaluaciones e
        JOIN usuarios u ON u.id_usuario = e.id_usuario WHERE e.id_evaluacion = :i
    """), {"i": id_evaluacion}).fetchone()
    if not f or f.perfil_json is None:
        raise HTTPException(404, "Esa evaluación no tiene reporte")
    return {"nombre": f.nombre, "perfil": leer_json(f.perfil_json)}


@app.get("/modelos")
def listar_modelos():
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
        http_options=types.HttpOptions(api_version=GEMINI_API_VERSION, timeout=30_000),
    )
    return [m.name for m in client.models.list()]