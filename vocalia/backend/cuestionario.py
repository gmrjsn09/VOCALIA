"""Catálogo de la UCV Chiclayo, banco de preguntas y lógica de puntajes (sin dependencias externas)."""
import math

UCV_NOMBRE = "Universidad César Vallejo (UCV) - Sede Chiclayo"
URL_CARRERAS_UCV = "https://www.ucv.edu.pe/programas/pregrados?modalidad=1"
URL_PREGRADO = "https://www.ucv.edu.pe/pregrado-presencial/"

F_EMP = "Facultad de Ciencias Empresariales"
F_ING = "Facultad de Ingeniería y Arquitectura"
F_SAL = "Facultad de Ciencias de la Salud"
F_DER = "Facultad de Derecho y Humanidades"
FACULTADES = [F_EMP, F_ING, F_SAL, F_DER]

# (carrera, facultad, área vocacional)
CARRERAS_UCV = [
    ("Administración de Empresas", F_EMP, "negocios"),
    ("Administración y Marketing", F_EMP, "negocios"),
    ("Administración y Negocios Internacionales", F_EMP, "negocios"),
    ("Administración en Turismo y Hotelería", F_EMP, "negocios"),
    ("Contabilidad", F_EMP, "negocios"),
    ("Economía y Finanzas", F_EMP, "negocios"),
    ("Arquitectura", F_ING, "arte"),
    ("Ingeniería Civil", F_ING, "tecnologia"),
    ("Ingeniería Industrial", F_ING, "tecnologia"),
    ("Ingeniería de Sistemas", F_ING, "tecnologia"),
    ("Ingeniería Mecánica Eléctrica", F_ING, "tecnologia"),
    ("Ingeniería Ambiental", F_ING, "ciencias"),
    ("Ingeniería Empresarial", F_ING, "negocios"),
    ("Ingeniería en Ciberseguridad", F_ING, "tecnologia"),
    ("Medicina Humana", F_SAL, "salud"),
    ("Enfermería", F_SAL, "salud"),
    ("Estomatología (Odontología)", F_SAL, "salud"),
    ("Psicología", F_SAL, "salud"),
    ("Nutrición", F_SAL, "salud"),
    ("Derecho", F_DER, "sociedad"),
    ("Ciencias de la Comunicación", F_DER, "arte"),
    ("Educación Inicial", F_DER, "educacion"),
    ("Educación Primaria", F_DER, "educacion"),
]
CATALOGO = {n.lower(): (f, a) for n, f, a in CARRERAS_UCV}
ORDEN_CARRERA = {n.lower(): i for i, (n, _, _) in enumerate(CARRERAS_UCV)}

# Páginas oficiales de cada carrera en la UCV (cada una muestra la malla curricular por ciclos).
# Se cargan al reiniciar el backend, solo en las carreras que todavía no tengan enlace.
MALLAS_URL = {
    "Administración de Empresas": URL_PREGRADO + "administracion",
    "Administración y Marketing": URL_PREGRADO + "administracion-y-marketing",
    "Administración y Negocios Internacionales": URL_PREGRADO + "administracion-negocios-internacionales",
    "Administración en Turismo y Hotelería": URL_PREGRADO + "administracion-turismo-y-hoteleria",
    "Contabilidad": URL_PREGRADO + "contabilidad",
    "Economía y Finanzas": URL_PREGRADO + "economia",
    "Arquitectura": URL_PREGRADO + "arquitectura",
    "Ingeniería Civil": URL_PREGRADO + "ingenieria-civil",
    "Ingeniería Industrial": URL_PREGRADO + "ingenieria-industrial",
    "Ingeniería de Sistemas": URL_PREGRADO + "ingenieria-de-sistemas",
    "Ingeniería Mecánica Eléctrica": URL_PREGRADO + "ingenieria-mecanica-electrica",
    "Ingeniería Ambiental": URL_PREGRADO + "ingenieria-ambiental",
    "Ingeniería Empresarial": URL_PREGRADO + "ingenieria-empresarial",
    "Ingeniería en Ciberseguridad": URL_PREGRADO + "ingenieria-de-ciberseguridad",
    "Medicina Humana": URL_PREGRADO + "medicina",
    "Enfermería": URL_PREGRADO + "enfermeria",
    "Estomatología (Odontología)": URL_PREGRADO + "estomatologia",
    "Psicología": URL_PREGRADO + "psicologia",
    "Nutrición": URL_PREGRADO + "nutricion",
    "Derecho": URL_PREGRADO + "derecho",
    "Ciencias de la Comunicación": URL_PREGRADO + "ciencias-de-la-comunicacion",
    "Educación Inicial": URL_PREGRADO + "educacion-inicial",
    "Educación Primaria": URL_PREGRADO + "educacion-primaria",
}

# Área secundaria de cada carrera (criterio propuesto; sirve para diferenciar carreras de una misma área)
SECUNDARIA = {
    "administración de empresas": "sociedad", "administración y marketing": "arte",
    "administración y negocios internacionales": "sociedad", "administración en turismo y hotelería": "arte",
    "contabilidad": "tecnologia", "economía y finanzas": "sociedad",
    "arquitectura": "tecnologia", "ingeniería civil": "ciencias", "ingeniería industrial": "negocios",
    "ingeniería de sistemas": "negocios", "ingeniería mecánica eléctrica": "ciencias",
    "ingeniería ambiental": "tecnologia", "ingeniería empresarial": "tecnologia",
    "ingeniería en ciberseguridad": "sociedad",
    "medicina humana": "ciencias", "enfermería": "educacion", "estomatología (odontología)": "ciencias",
    "psicología": "sociedad", "nutrición": "ciencias",
    "derecho": "negocios", "ciencias de la comunicación": "sociedad",
    "educación inicial": "salud", "educación primaria": "sociedad",
}

AREAS = {
    "tecnologia": {"nombre": "Tecnología e Ingeniería", "icono": "💻", "color": "#22D3EE",
                   "holland": "Realista e Investigador",
                   "descripcion": "Programar, crear sistemas, entender cómo funcionan las máquinas y resolver problemas técnicos."},
    "salud": {"nombre": "Salud y Bienestar", "icono": "🩺", "color": "#34D399",
              "holland": "Social e Investigador",
              "descripcion": "Cuidar a las personas, entender el cuerpo y la mente, y acompañar en su bienestar."},
    "negocios": {"nombre": "Negocios y Gestión", "icono": "📊", "color": "#F59E0B",
                 "holland": "Emprendedor y Convencional",
                 "descripcion": "Dirigir equipos, manejar dinero, crear empresas y organizar proyectos."},
    "sociedad": {"nombre": "Derecho y Ciencias Sociales", "icono": "⚖️", "color": "#A78BFA",
                 "holland": "Emprendedor y Social",
                 "descripcion": "Defender ideas con argumentos, conocer las leyes y trabajar por la justicia."},
    "arte": {"nombre": "Arte, Diseño y Comunicación", "icono": "🎨", "color": "#F472B6",
             "holland": "Artístico",
             "descripcion": "Crear, diseñar espacios o imágenes y comunicar mensajes a mucha gente."},
    "educacion": {"nombre": "Educación y Servicio Social", "icono": "🎓", "color": "#60A5FA",
                  "holland": "Social",
                  "descripcion": "Enseñar, guiar a niños y adolescentes y mejorar la vida de la comunidad."},
    "ciencias": {"nombre": "Ciencias y Ambiente", "icono": "🌱", "color": "#84CC16",
                 "holland": "Investigador y Realista",
                 "descripcion": "Investigar, cuidar la naturaleza y buscar soluciones a la contaminación."},
}

# Las 5 opciones de respuesta (no cambiar)
ESCALAS = {
    "intereses": {1: "Nada", 2: "Poco", 3: "Neutral", 4: "Me gusta", 5: "Me apasiona"},
    "habilidades": {1: "Muy bajo", 2: "Bajo", 3: "Medio", 4: "Alto", 5: "Muy alto"},
}

FUNDAMENTO = {
    "texto": ("Esta evaluación organiza tus respuestas en 7 áreas vocacionales, inspiradas en el modelo de "
              "intereses de John Holland (tipos RIASEC), y las relaciona con las 23 carreras de la UCV sede "
              "Chiclayo. Es una herramienta de orientación: no es una prueba psicométrica estandarizada ni "
              "reemplaza la atención de un psicólogo."),
    "referencias": [
        "Holland, J. L. (1997). Making Vocational Choices: A Theory of Vocational Personalities and Work "
        "Environments (3.ª ed.). Psychological Assessment Resources.",
        "O*NET Interest Profiler (Departamento de Trabajo de EE. UU.), basado en el modelo RIASEC de Holland.",
    ],
    "estado": "Propuesta pendiente de validación por juicio de expertos.",
}

# ---------------- INTERESES (3 por tema) ----------------
INTERESES = {
    "tecnologia": [
        "Me llama la atención programar, crear aplicaciones o videojuegos.",
        "Me gusta armar o desarmar aparatos, redes o circuitos para entender cómo funcionan.",
        "Disfruto resolver problemas de lógica, matemática o ingeniería.",
    ],
    "salud": [
        "Me interesa comprender el cuerpo humano y cómo se curan las enfermedades.",
        "Me sentiría bien atendiendo a personas enfermas o en una emergencia.",
        "Me atraen temas como la nutrición, la psicología o el bienestar emocional.",
    ],
    "negocios": [
        "Me motiva liderar equipos y organizar proyectos.",
        "Me interesa saber cómo funcionan las empresas, las ventas y el dinero.",
        "Me veo creando mi propio negocio o emprendimiento.",
    ],
    "sociedad": [
        "Me interesa interpretar leyes y defender ideas con argumentos.",
        "Disfruto debatir sobre temas sociales, políticos o de justicia.",
        "Me atrae investigar cómo piensan y se organizan las sociedades.",
    ],
    "arte": [
        "Disfruto dibujar, diseñar, fotografiar o crear contenido visual.",
        "Me gusta escribir, hablar en público o comunicar mensajes en los medios.",
        "Me atraen la música, el cine, la moda o la arquitectura creativa.",
    ],
    "educacion": [
        "Me gusta explicar temas a otros y ver que aprenden.",
        "Me veo trabajando con niños o adolescentes para guiarlos.",
        "Quisiera mejorar la vida de mi comunidad con proyectos sociales.",
    ],
    "ciencias": [
        "Me interesa cuidar el medio ambiente y la naturaleza.",
        "Me interesa entender cómo se pueden tratar el agua, los residuos y la contaminación.",
        "Disfruto hacer experimentos e investigar en laboratorio o en campo.",
    ],
}

# Preguntas finales de profundización (evaluación adaptativa): solo para tu área con más interés
ADAPTATIVAS = {
    "tecnologia": [
        "Me gustaría analizar grandes cantidades de datos para descubrir patrones.",
        "Me veo diseñando sistemas, estructuras o máquinas que usen miles de personas.",
        "Me interesa saber cómo se protegen los sistemas y la información de los ataques informáticos.",
    ],
    "salud": [
        "Podría afrontar situaciones médicas difíciles si eso ayuda a salvar a alguien.",
        "Estudiaría muchos años para especializarme en el área de salud.",
        "Me gustaría acompañar emocionalmente a personas con problemas personales.",
    ],
    "negocios": [
        "Disfruto negociar, convencer y cerrar acuerdos.",
        "Me interesa entender los números: costos, ganancias y presupuestos.",
        "Me atraen el turismo, los hoteles o el comercio con otros países.",
    ],
    "sociedad": [
        "Leería un documento largo para encontrar un argumento clave.",
        "Me indigna la injusticia y quiero actuar para corregirla.",
        "Me gustaría trabajar en el Estado, en políticas públicas o en la diplomacia.",
    ],
    "arte": [
        "Pasaría horas perfeccionando un diseño o una obra hasta que quede bien.",
        "Me gustaría que mis creaciones las vea mucha gente.",
        "Observo con detalle los colores, las formas y los espacios a mi alrededor.",
    ],
    "educacion": [
        "Tengo paciencia para repetir una explicación las veces que haga falta.",
        "Me ilusiona ser un modelo o guía para otras personas.",
        "Me gustaría diseñar programas para ayudar a grupos vulnerables.",
    ],
    "ciencias": [
        "Me gustaría trabajar en el campo o en plantas de tratamiento tomando muestras y mediciones.",
        "Me interesa buscar soluciones al cambio climático o a la contaminación.",
        "Me atrae analizar muestras, suelos o aguas para mejorar su calidad.",
    ],
}

# ---------------- HABILIDADES (2 por tema; la primera área de la lista es su tema) ----------------
HABILIDADES = [
    {"id": "H01", "nombre": "Razonamiento lógico y matemático",
     "texto": "Resuelvo con facilidad problemas de matemática y lógica.",
     "areas": ["tecnologia", "negocios"],
     "consejo": "Practica ejercicios de lógica y matemática 20 minutos al día (por ejemplo en Khan Academy)."},
    {"id": "H02", "nombre": "Manejo de tecnología",
     "texto": "Aprendo rápido a usar programas, apps y dispositivos nuevos.",
     "areas": ["tecnologia"],
     "consejo": "Explora cursos gratuitos de ofimática, programación o diseño digital."},
    {"id": "H03", "nombre": "Empatía y escucha",
     "texto": "Entiendo cómo se sienten los demás y sé escucharlos.",
     "areas": ["salud", "educacion"],
     "consejo": "Practica la escucha activa y conversa con personas de distintos contextos."},
    {"id": "H04", "nombre": "Manejo del estrés",
     "texto": "Mantengo la calma cuando hay presión o imprevistos.",
     "areas": ["salud"],
     "consejo": "Prueba técnicas de respiración y organiza tu tiempo para reducir la presión."},
    {"id": "H05", "nombre": "Liderazgo",
     "texto": "Organizo a mi grupo y tomo la iniciativa cuando hace falta.",
     "areas": ["negocios", "sociedad"],
     "consejo": "Postula a delegado o lidera un proyecto pequeño en tu colegio."},
    {"id": "H06", "nombre": "Organización y disciplina",
     "texto": "Planifico mi tiempo y cumplo mis tareas sin que me lo recuerden.",
     "areas": ["negocios", "ciencias"],
     "consejo": "Usa una agenda semanal con metas pequeñas y revísala cada día."},
    {"id": "H07", "nombre": "Comunicación oral",
     "texto": "Me expreso con claridad cuando hablo frente a un grupo.",
     "areas": ["sociedad", "educacion", "negocios"],
     "consejo": "Ofrécete a exponer en clase o participa en debates y talleres de oratoria."},
    {"id": "H08", "nombre": "Redacción y comprensión lectora",
     "texto": "Escribo y entiendo textos largos sin dificultad.",
     "areas": ["sociedad", "arte"],
     "consejo": "Lee un libro o artículo por semana y escribe un resumen corto."},
    {"id": "H09", "nombre": "Creatividad",
     "texto": "Se me ocurren ideas originales para resolver problemas o crear algo nuevo.",
     "areas": ["arte", "tecnologia"],
     "consejo": "Dedica tiempo a proyectos libres: dibujar, escribir, construir o inventar soluciones."},
    {"id": "H10", "nombre": "Sentido estético y visual",
     "texto": "Noto fácilmente si un diseño, un espacio o una imagen está bien equilibrado.",
     "areas": ["arte"],
     "consejo": "Observa diseños, edificios y fotografías, y practica bocetos de lo que te llame la atención."},
    {"id": "H11", "nombre": "Paciencia para enseñar",
     "texto": "Puedo explicar algo varias veces, con calma, hasta que la otra persona lo entienda.",
     "areas": ["educacion"],
     "consejo": "Ayuda a un compañero con un tema que domines o da reforzamiento a niños."},
    {"id": "H12", "nombre": "Trabajo en equipo",
     "texto": "Trabajo bien con otros y ayudo a que el grupo logre sus metas.",
     "areas": ["educacion", "salud", "negocios"],
     "consejo": "Únete a proyectos grupales, deportes o voluntariados."},
    {"id": "H13", "nombre": "Observación y análisis",
     "texto": "Observo con detalle, hago preguntas y busco explicaciones.",
     "areas": ["ciencias", "salud"],
     "consejo": "Haz experimentos sencillos y registra lo que observas."},
    {"id": "H14", "nombre": "Habilidad práctica",
     "texto": "Soy bueno armando, reparando o trabajando con las manos o en el campo.",
     "areas": ["ciencias", "tecnologia"],
     "consejo": "Participa en talleres de reparación, huerto o robótica."},
]

AREA_PALABRAS = {
    "ciencias": ["biolog", "biotecn", "ambient", "química", "quimica", "física", "fisica", "forestal"],
    "salud": ["medicin", "enfermer", "odontolog", "estomatolog", "psicolog", "nutrici", "farmac", "salud"],
    "sociedad": ["derecho", "ciencias pol", "sociolog", "antropolog", "relaciones intern", "historia"],
    "educacion": ["educaci", "pedagog", "trabajo social", "docen"],
    "arte": ["arquitect", "diseño", "comunicaci", "periodis", "audiovis", "publicidad"],
    "negocios": ["administr", "negocio", "contab", "econom", "marketing", "finanz", "turismo", "empresa"],
    "tecnologia": ["sistemas", "informátic", "software", "computaci", "tecnolog", "industrial",
                   "electr", "mecán", "civil", "redes", "ciberseg", "ingenier"],
}

BASE_INTERESES = []
for _a in AREAS:
    for _t in INTERESES[_a]:
        BASE_INTERESES.append({"id": f"I{len(BASE_INTERESES) + 1:02d}", "texto": _t, "area": _a})
BASE_AREA = {q["id"]: q["area"] for q in BASE_INTERESES}

PESO_INTERES = 0.65
PESO_HABILIDAD = 0.35

# Contraste de porcentajes: la primera opción debe destacar claramente sobre las demás
RATIO_AREAS, ESCALA_AREAS = 0.75, 20
RATIO_CARRERAS, ESCALA_CARRERAS = 0.62, 20


def separar(valores, ratio, escala):
    """Convierte puntajes directos (0-100) en porcentajes relativos con mucha separación.
    El orden se mantiene igual: solo se amplía la diferencia entre la 1.ª opción y las demás."""
    if not valores:
        return []
    r0 = max(valores)
    a0 = min(97, max(50, 55 + 0.52 * r0))
    distintos = sorted(set(valores), reverse=True)
    out = []
    for v in valores:
        rango = distintos.index(v)
        f = min(ratio ** rango, math.exp(-(r0 - v) / escala))
        out.append(max(3, int(round(a0 * f))))
    return out


def facultad_de(nombre):
    cat = CATALOGO.get((nombre or "").strip().lower())
    return cat[0] if cat else None


def area_de_carrera(nombre, area_conocimiento=""):
    cat = CATALOGO.get((nombre or "").strip().lower())
    if cat:
        return cat[1]
    for texto in (nombre or "", area_conocimiento or ""):
        t = texto.lower()
        for area in ("ciencias", "salud", "sociedad", "educacion", "arte", "negocios", "tecnologia"):
            if any(p in t for p in AREA_PALABRAS[area]):
                return area
    return None


def cuestionario_base():
    temas = []
    for area, info in AREAS.items():
        temas.append({
            "area": area, "titulo": info["nombre"], "icono": info["icono"], "color": info["color"],
            "descripcion": info["descripcion"],
            "bloques": [
                {"clave": "intereses", "titulo": "Lo que te atrae", "escala": ESCALAS["intereses"],
                 "preguntas": [{"id": q["id"], "texto": q["texto"]} for q in BASE_INTERESES if q["area"] == area]},
                {"clave": "habilidades", "titulo": "Lo que se te da bien", "escala": ESCALAS["habilidades"],
                 "preguntas": [{"id": h["id"], "texto": h["texto"]} for h in HABILIDADES if h["areas"][0] == area]},
            ],
        })
    return {"areas": AREAS, "temas": temas, "escala_adaptativa": ESCALAS["intereses"], "fundamento": FUNDAMENTO}


def _valor(v):
    try:
        return max(1, min(5, int(v)))
    except (TypeError, ValueError):
        return None


def _limpiar(resp):
    out = {}
    for k, v in (resp or {}).items():
        n = _valor(v)
        if n is not None:
            out[str(k)] = n
    return out


def _media(vals):
    return sum(vals) / len(vals) if vals else None


def _area_interes(qid):
    if qid.startswith("A_"):
        partes = qid.split("_")
        return partes[1] if len(partes) > 2 else None
    return BASE_AREA.get(qid)


def preguntas_adaptativas(resp, n_areas=1):
    """Elige el área con más interés y devuelve preguntas de profundización."""
    resp = _limpiar(resp)
    prom = {}
    for a in AREAS:
        vals = [v for k, v in resp.items() if BASE_AREA.get(k) == a]
        prom[a] = _media(vals) or 0
    top = sorted(AREAS, key=lambda a: prom[a], reverse=True)[:n_areas]
    out = []
    for area in top:
        for i, texto in enumerate(ADAPTATIVAS[area], start=1):
            out.append({"id": f"A_{area}_{i}", "texto": texto, "area": area})
    return out


def calcular_puntajes(resp):
    """Devuelve las 7 áreas ordenadas. 'directo' es el puntaje medido (0-100);
    'puntaje' es el porcentaje relativo, con mayor separación entre la 1.ª área y las demás."""
    resp = _limpiar(resp)
    inter = {a: [] for a in AREAS}
    hab = {a: [] for a in AREAS}
    for qid, v in resp.items():
        a = _area_interes(qid)
        if a in inter:
            inter[a].append(v)
    for h in HABILIDADES:
        if h["id"] in resp:
            for a in h["areas"]:
                hab[a].append(resp[h["id"]])
    claves, directos = [], []
    for a in AREAS:
        comps = []
        if inter[a]:
            comps.append((PESO_INTERES, _media(inter[a])))
        if hab[a]:
            comps.append((PESO_HABILIDAD, _media(hab[a])))
        if comps:
            w = sum(c[0] for c in comps)
            pts = sum(wt * (v - 1) / 4 * 100 for wt, v in comps) / w
        else:
            pts = 0
        claves.append(a)
        directos.append(int(round(pts)))
    relativos = separar(directos, RATIO_AREAS, ESCALA_AREAS)
    res = []
    for a, d, r in zip(claves, directos, relativos):
        info = AREAS[a]
        res.append({"clave": a, "nombre": info["nombre"], "icono": info["icono"], "color": info["color"],
                    "directo": d, "puntaje": r})
    res.sort(key=lambda x: (x["directo"], x["puntaje"]), reverse=True)
    return res


def habilidades_ordenadas(resp):
    resp = _limpiar(resp)
    lista = [{"id": h["id"], "nombre": h["nombre"], "valor": resp[h["id"]]}
             for h in HABILIDADES if h["id"] in resp]
    lista.sort(key=lambda x: x["valor"], reverse=True)
    return lista


def calcular_brechas(resp, areas_top):
    """Habilidades relevantes para tus áreas top en las que te calificaste bajo."""
    resp = _limpiar(resp)
    cand = []
    for h in HABILIDADES:
        rel = len(set(h["areas"]) & set(areas_top))
        if h["id"] in resp and resp[h["id"]] <= 3 and rel:
            cand.append((resp[h["id"]], -rel, h))
    cand.sort(key=lambda x: (x[0], x[1]))
    return [{"nombre": h["nombre"], "valor": v, "consejo": h["consejo"]} for v, _, h in cand[:4]]


def perfil_respaldo(resp, carreras):
    """Perfil calculado sin IA (se usa si Gemini no responde)."""
    areas = calcular_puntajes(resp)
    top = areas[:2]
    directo = {a["clave"]: a["directo"] for a in areas}
    promedio = sum(directo.values()) / len(directo)
    habs = habilidades_ordenadas(resp)
    brechas = calcular_brechas(resp, [a["clave"] for a in top])

    candidatas = []
    for c in carreras:
        nombre = c["nombre"].strip().lower()
        area = area_de_carrera(c["nombre"], c.get("area_conocimiento") or "")
        sec = SECUNDARIA.get(nombre)
        if area:
            base = directo[area]
            if sec in directo:
                base = 0.7 * base + 0.3 * directo[sec]
            motivo = (f"Combina tu afinidad por {AREAS[area]['nombre']} con tu interés en {AREAS[sec]['nombre']}."
                      if sec in directo else f"Coincide con tu afinidad por {AREAS[area]['nombre']}.")
        else:
            base = max(0, promedio - 15)
            motivo = "Carrera de la UCV Chiclayo."
        base -= 0.01 * ORDEN_CARRERA.get(nombre, 99)  # desempate estable
        candidatas.append({"nombre": c["nombre"], "universidad": c.get("universidad") or "",
                           "afinidad": base, "motivo": motivo, "_area": area})
    candidatas.sort(key=lambda x: x["afinidad"], reverse=True)
    elegidas, cuenta = [], {}
    for c in candidatas:
        if cuenta.get(c["_area"], 0) >= 2:
            continue
        cuenta[c["_area"]] = cuenta.get(c["_area"], 0) + 1
        elegidas.append({k: v for k, v in c.items() if k != "_area"})
        if len(elegidas) == 3:
            break

    fort = [h["nombre"] for h in habs[:3]]
    resumen = (f"Tu perfil destaca en {top[0]['nombre']} ({top[0]['puntaje']}%) y "
               f"{top[1]['nombre']} ({top[1]['puntaje']}%). "
               + (f"Tus mayores fortalezas son {', '.join(fort)}." if fort else ""))
    plan = [
        f"Revisa las carreras de {top[0]['nombre']} en la pestaña Oferta educativa y abre su malla curricular.",
        "Conversa con estudiantes o profesionales de esas carreras para conocer su día a día.",
        (brechas[0]["consejo"] if brechas else
         "Asiste a las charlas y ferias vocacionales de la UCV y otras universidades de Chiclayo."),
    ]
    return {"resumen": resumen, "fortalezas": fort, "carreras": elegidas,
            "brechas": [f"{b['nombre']}: {b['consejo']}" for b in brechas], "plan": plan}


def _a_int(v):
    try:
        return int(float(str(v).replace("%", "")))
    except ValueError:
        return 0


def normalizar_ia(data, validas=None):
    """Valida el JSON de Gemini. Solo acepta carreras que estén en la lista de la UCV."""
    if not isinstance(data, dict) or not data.get("resumen"):
        raise ValueError("Respuesta incompleta de la IA")
    carreras = []
    for c in (data.get("carreras") or [])[:5]:
        if not (isinstance(c, dict) and c.get("nombre")):
            continue
        if validas and str(c["nombre"]).strip().lower() not in validas:
            continue
        carreras.append({"nombre": str(c["nombre"]).strip(), "universidad": str(c.get("universidad", "")),
                         "afinidad": max(0, min(100, _a_int(c.get("afinidad", 0)))),
                         "motivo": str(c.get("motivo", ""))})
        if len(carreras) == 3:
            break
    if not carreras:
        raise ValueError("La IA no devolvió carreras válidas de la UCV")

    def lista(k, n):
        v = data.get(k)
        return [str(x) for x in v if x][:n] if isinstance(v, list) else []

    return {"resumen": str(data["resumen"]), "fortalezas": lista("fortalezas", 4),
            "carreras": carreras, "brechas": lista("brechas", 4), "plan": lista("plan", 4)}


def completar_perfil(parcial, resp, nivel, modo):
    perfil = dict(parcial)
    carreras = sorted(perfil.get("carreras", []), key=lambda c: c["afinidad"], reverse=True)
    nuevos = separar([c["afinidad"] for c in carreras], RATIO_CARRERAS, ESCALA_CARRERAS)
    for c, n in zip(carreras, nuevos):
        c["afinidad_directa"] = int(round(c["afinidad"]))
        c["afinidad"] = n
    perfil["carreras"] = carreras
    perfil["areas"] = calcular_puntajes(resp)
    perfil["habilidades"] = [{"nombre": h["nombre"], "valor": h["valor"]}
                             for h in habilidades_ordenadas(resp)]
    perfil["nivel_adaptativo"] = nivel
    perfil["modo"] = modo
    return perfil


def construir_prompt(usuario, resp, carreras):
    resp = _limpiar(resp)
    areas = calcular_puntajes(resp)
    top = [a["clave"] for a in areas[:2]]
    l_areas = "\n".join(f"- {a['nombre']}: {a['directo']}/100" for a in areas)
    l_hab = "\n".join(f"- {h['nombre']}: {h['valor']}/5" for h in habilidades_ordenadas(resp))
    brechas = calcular_brechas(resp, top)
    l_br = "\n".join(f"- {b['nombre']} ({b['valor']}/5)" for b in brechas) or "- Sin brechas importantes"
    lineas = []
    for c in carreras:
        extra = []
        if c.get("demanda_laboral"):
            extra.append(f"demanda {c['demanda_laboral']}")
        if c.get("salario_promedio"):
            extra.append(f"salario promedio S/ {c['salario_promedio']:.0f}")
        sufijo = f" | {', '.join(extra)}" if extra else ""
        lineas.append(f"- {c['nombre']} ({c.get('facultad') or 'UCV'}){sufijo}")
    l_car = "\n".join(lineas)
    edad = f", {usuario.get('edad')} años" if usuario.get("edad") else ""
    return f"""
Actúa como un orientador vocacional experto de la Universidad César Vallejo (UCV), sede Chiclayo, Perú. Analiza el perfil de este estudiante de secundaria y recomienda carreras de la UCV.

Estudiante: {usuario.get('nombre')} ({usuario.get('colegio')}, {usuario.get('grado')}{edad})

Afinidad calculada por área (0-100):
{l_areas}

Autoevaluación de habilidades (1-5):
{l_hab}

Brechas de competencias detectadas para sus áreas principales:
{l_br}

Carreras disponibles en la UCV Chiclayo (recomienda SOLO de esta lista y usa el nombre exacto):
{l_car}

Responde SOLO con un JSON válido con esta estructura exacta:
{{
  "resumen": "síntesis del perfil en 3 o 4 oraciones, en segunda persona, tono motivador",
  "fortalezas": ["fortaleza 1", "fortaleza 2", "fortaleza 3"],
  "carreras": [
    {{"nombre": "nombre exacto de la lista", "universidad": "Universidad César Vallejo", "afinidad": 0-100, "motivo": "una frase que justifique la recomendación"}}
  ],
  "brechas": ["habilidad a reforzar y cómo hacerlo", "otra brecha y cómo reforzarla"],
  "plan": ["paso concreto 1", "paso concreto 2", "paso concreto 3"]
}}
Incluye exactamente 3 carreras de mayor a menor afinidad, coherentes con los puntajes por área.
"""