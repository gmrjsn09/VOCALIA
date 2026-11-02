import os
import re
import html
import math
from datetime import datetime
import requests
import pandas as pd
import streamlit as st

API = os.getenv("API_URL", "https://vocalia-c69r.onrender.com")
URL_UCV = "https://www.ucv.edu.pe/programas/pregrados?modalidad=1"
ORDEN = ["tecnologia", "salud", "negocios", "sociedad", "arte", "educacion", "ciencias"]
CORTO = {"tecnologia": "Tecnología", "salud": "Salud", "negocios": "Negocios",
         "sociedad": "Derecho", "arte": "Arte", "educacion": "Educación", "ciencias": "Ciencias"}
FACULTADES = ["Facultad de Ciencias Empresariales", "Facultad de Ingeniería y Arquitectura",
              "Facultad de Ciencias de la Salud", "Facultad de Derecho y Humanidades"]
COLORES = ["#F59E0B", "#22D3EE", "#A78BFA"]

st.set_page_config(page_title="Vocacional IA · UCV Chiclayo", page_icon="🧭", layout="centered")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;700;800&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"], .stMarkdown, label, p { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Sora', sans-serif !important; }
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
.block-container { padding-top: 1.6rem; max-width: 900px; }
.hero { background: linear-gradient(135deg, #0F4C5C 0%, #1D4ED8 55%, #7C3AED 100%);
        border-radius: 22px; padding: 30px 34px; margin-bottom: 18px; color: #fff; position: relative; overflow: hidden; }
.hero:after { content: "🧭"; position: absolute; right: 26px; top: 10px; font-size: 90px; opacity: .2; }
.hero h1 { margin: 0; font-size: 2.3rem; font-weight: 800; color: #fff; }
.hero p { margin: 6px 0 0; font-size: 1.02rem; opacity: .92; }
.card { background: #111B2E; border: 1px solid #22304A; border-radius: 16px; padding: 18px 22px; margin-bottom: 14px; }
.card .tag { color: #22D3EE; font-weight: 700; font-size: .95rem; margin-bottom: 8px; font-family: 'Sora', sans-serif; }
.quote { border-left: 6px solid #22D3EE; line-height: 1.65; }
.tema { border-radius: 16px; padding: 16px 22px; margin: 4px 0 14px; background: #111B2E; border: 1px solid #22304A; }
.tema h3 { margin: 0 0 4px; }
.tema p { margin: 0; color: #9FB0C8; font-size: .95rem; }
.bloque { font-family: 'Sora', sans-serif; font-weight: 700; color: #FCD34D; margin: 14px 0 4px; font-size: .95rem; }
.top { background: linear-gradient(135deg, #F59E0B, #EF4444); border-radius: 20px; padding: 22px 26px; color: #fff;
       display: flex; gap: 22px; align-items: center; margin: 6px 0 16px; }
.top h2 { margin: 2px 0 4px; color: #fff; font-size: 1.5rem; }
.top .mini { font-size: .85rem; font-weight: 600; opacity: .9; }
.ring { width: 104px; height: 104px; border-radius: 50%; display: grid; place-items: center; flex: none; }
.ring span { width: 78px; height: 78px; border-radius: 50%; background: rgba(11,18,32,.88); display: grid;
             place-items: center; font-family: 'Sora', sans-serif; font-weight: 800; font-size: 1.3rem; color: #fff; }
.row { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; margin-top: 10px; }
.row b { font-family: 'Sora', sans-serif; font-size: .98rem; }
.row .pct { font-weight: 800; }
.sub { color: #9FB0C8; font-size: .9rem; margin: 2px 0 8px; }
.bar { background: #22304A; border-radius: 99px; height: 9px; overflow: hidden; margin-top: 5px; }
.bar div { height: 100%; border-radius: 99px; }
.why2 { color: #C9D6E8; font-size: .92rem; margin-top: 10px; }
.pill { display: inline-block; background: rgba(167,139,250,.16); color: #D8CCFF; border: 1px solid rgba(167,139,250,.45);
        border-radius: 14px; padding: 7px 14px; margin: 0 8px 8px 0; font-size: .9rem; }
.pill.ok { background: rgba(52,211,153,.14); color: #A7F3D0; border-color: rgba(52,211,153,.45); }
.chip { display: inline-block; background: #1A2740; color: #C9D6E8; border-radius: 99px; padding: 4px 12px;
        margin: 8px 8px 0 0; font-size: .82rem; border: 1px solid #22304A; }
.btn { display: inline-block; margin-top: 12px; padding: 8px 16px; border-radius: 12px; font-weight: 700; font-size: .9rem;
       background: linear-gradient(135deg, #1D4ED8, #7C3AED); color: #fff !important; text-decoration: none !important; }
.btn.light { background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.6); }
.step { display: flex; gap: 14px; align-items: flex-start; background: #111B2E; border: 1px solid #22304A;
        border-radius: 14px; padding: 14px 18px; margin-bottom: 10px; }
.step .n { background: linear-gradient(135deg, #F59E0B, #EF4444); color: #fff; font-weight: 800; border-radius: 50%;
           width: 30px; height: 30px; display: grid; place-items: center; flex: none; }
.areatag { display: inline-block; border-radius: 99px; padding: 3px 12px; font-size: .8rem; font-weight: 600;
           background: rgba(245,158,11,.15); color: #FCD34D; margin-bottom: 4px; }
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
    background: linear-gradient(135deg, #F59E0B, #EF4444); border: 0; color: #fff; border-radius: 12px;
    font-weight: 700; padding: .6rem 1.5rem; }
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"] { border-radius: 12px; }
[data-testid="stForm"] { border: 1px solid #22304A; border-radius: 18px; padding: 20px; }
.reporte { background: linear-gradient(135deg, #0B1F3A 0%, #14325E 100%); border: 1px solid rgba(201,162,39,.45);
           border-left: 5px solid #C9A227; border-radius: 16px; padding: 20px 26px; margin: 8px 0 12px; }
.reporte .r-tag { color: #C9A227; font-weight: 700; letter-spacing: 2.5px; font-size: .72rem; }
.reporte h3 { color: #F4E7C5; margin: 4px 0 6px; font-size: 1.25rem; }
.reporte p { color: #B8C4D6; margin: 0; font-size: .95rem; line-height: 1.55; }
[data-testid="stDownloadButton"] button { background: linear-gradient(135deg, #0B1F3A, #1E3A6E); color: #F4E7C5;
    border: 1px solid #C9A227; border-radius: 12px; font-weight: 700; padding: .65rem 1.8rem; letter-spacing: .3px; }
[data-testid="stDownloadButton"] button p { color: inherit; }
[data-testid="stDownloadButton"] button:hover { border-color: #E8CF86; color: #fff; box-shadow: 0 6px 22px rgba(201,162,39,.28); }
.avatar { width: 52px; height: 52px; border-radius: 50%; display: grid; place-items: center;
          background: linear-gradient(135deg, #1D4ED8, #7C3AED); color: #fff; font-weight: 800; font-size: 1.3rem; margin-bottom: 8px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------- utilidades ----------------------------------
def esc(x):
    return html.escape(str(x if x is not None else ""))


def pct(v):
    try:
        return max(0, min(100, int(float(str(v).replace("%", "")))))
    except ValueError:
        return 0


def api(metodo, ruta, **kw):
    try:
        r = requests.request(metodo, f"{API}{ruta}", timeout=240, **kw)
    except requests.ConnectionError:
        st.error("No se pudo conectar con el servidor. ¿Está encendido el backend?")
        return None
    except requests.Timeout:
        st.error("El servidor tardó demasiado en responder. Revisa la terminal del backend.")
        return None
    if r.status_code >= 400:
        try:
            detalle = r.json().get("detail", "Ocurrió un error")
        except ValueError:
            detalle = f"Error {r.status_code}: revisa la terminal del backend"
        st.error(detalle)
        return None
    try:
        return r.json()
    except ValueError:
        st.error("El servidor respondió algo inesperado. Revisa la terminal del backend.")
        return None


def boton_malla(c, claro=False):
    """Botón que abre la malla curricular (o la página de carreras) de la UCV."""
    url = c.get("url_malla") or URL_UCV
    if "admision/carreras-profesionales" in url:  # enlace antiguo que ya no existe
        url = URL_UCV
    texto = "📄 Ver malla curricular" if c.get("malla_directa") else "🔎 Ver carreras en la web de la UCV"
    clase = "btn light" if claro else "btn"
    return f'<a class="{clase}" href="{esc(url)}" target="_blank" rel="noopener noreferrer">{texto}</a>'


def radar_svg(areas, size=360):
    por = {a["clave"]: a for a in areas}
    ejes = [por[k] for k in ORDEN if k in por]
    n = len(ejes)
    if n < 3:
        return ""
    cx = cy = size / 2
    R = size / 2 - 78

    def pt(i, f):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        return cx + R * f * math.cos(ang), cy + R * f * math.sin(ang)

    s = [f'<svg viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" '
         f'style="width:100%;max-width:{size}px;display:block;margin:auto">']
    for nivel in (0.25, 0.5, 0.75, 1):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, nivel) for i in range(n)))
        s.append(f'<polygon points="{pts}" fill="none" stroke="#22304A" stroke-width="1"/>')
    for i in range(n):
        x, y = pt(i, 1)
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#22304A" stroke-width="1"/>')
    datos = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, a["puntaje"] / 100) for i, a in enumerate(ejes)))
    s.append(f'<polygon points="{datos}" fill="rgba(245,158,11,.35)" stroke="#F59E0B" stroke-width="2.5"/>')
    for i, a in enumerate(ejes):
        x, y = pt(i, a["puntaje"] / 100)
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{a["color"]}"/>')
        lx, ly = pt(i, 1.2)
        anc = "middle" if abs(lx - cx) < 12 else ("start" if lx > cx else "end")
        s.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anc}" font-size="12" fill="#C9D6E8" '
                 f'font-family="Inter,sans-serif">{a["icono"]} {CORTO.get(a["clave"], "")}</text>')
        s.append(f'<text x="{lx:.1f}" y="{ly + 14:.1f}" text-anchor="{anc}" font-size="11" font-weight="700" '
                 f'fill="{a["color"]}" font-family="Inter,sans-serif">{a["puntaje"]}%</text>')
    s.append("</svg>")
    return "".join(s)


def barras_areas(areas):
    return "".join(
        f'<div class="row"><b>{esc(a["icono"])} {esc(a["nombre"])}</b>'
        f'<span class="pct" style="color:{a["color"]}">{a["puntaje"]}%</span></div>'
        f'<div class="bar"><div style="width:{a["puntaje"]}%;background:{a["color"]}"></div></div>'
        for a in areas)


def chips_mercado(c):
    out = ""
    if c.get("demanda_laboral"):
        out += f'<span class="chip">📈 Demanda: {esc(c["demanda_laboral"])}</span>'
    if c.get("salario_promedio"):
        out += f'<span class="chip">💰 Salario promedio: S/ {c["salario_promedio"]:,.0f}</span>'
    if c.get("sectores_clave"):
        out += f'<span class="chip">🏭 {esc(c["sectores_clave"])}</span>'
    return out


def reporte_html(p, nombre):
    hoy = datetime.now().strftime("%d/%m/%Y")
    carreras = p.get("carreras", [])
    top = carreras[0] if carreras else {}
    filas_areas = "".join(
        f"<tr><td class='n'>{esc(a['nombre'])}</td>"
        f"<td class='b'><div class='bar'><i style='width:{a['puntaje']}%'></i></div></td>"
        f"<td class='v'>{a['puntaje']}%</td></tr>" for a in p.get("areas", []))
    lista_carreras = "".join(
        f"<div class='c'><div class='cn'>{i}</div><div class='ct'><b>{esc(c['nombre'])}</b>"
        f"<span class='uni'>{esc(c.get('facultad') or c.get('universidad', ''))}</span>"
        f"<p>{esc(c.get('motivo', ''))}</p><div class='bar'><i style='width:{pct(c['afinidad'])}%'></i></div></div>"
        f"<div class='cv'>{pct(c['afinidad'])}%</div></div>" for i, c in enumerate(carreras, start=1))
    lista = lambda k: "".join(f"<li>{esc(x)}</li>" for x in p.get(k, []))
    css = (
        "@page{margin:14mm}*{box-sizing:border-box}"
        "body{margin:0;background:#EEF0F3;font-family:'Segoe UI',Arial,sans-serif;color:#1F2937;"
        "-webkit-print-color-adjust:exact;print-color-adjust:exact}"
        ".page{max-width:800px;margin:28px auto;background:#fff;box-shadow:0 8px 30px rgba(11,31,58,.12)}"
        ".head{background:#0B1F3A;color:#fff;padding:30px 40px;border-bottom:4px solid #C9A227}"
        ".brand{letter-spacing:3px;font-size:11px;color:#C9A227;font-weight:700}"
        ".head h1{font-family:Georgia,'Times New Roman',serif;font-weight:400;font-size:32px;margin:8px 0 6px}"
        ".meta{margin:0;color:#B8C4D6;font-size:14px}"
        ".body{padding:30px 40px 36px}"
        ".hero{display:flex;justify-content:space-between;align-items:center;gap:20px;background:#F6F1E4;"
        "border-left:5px solid #C9A227;padding:20px 24px;border-radius:4px}"
        ".eyebrow{font-size:11px;letter-spacing:2px;color:#8A6D1F;font-weight:700}"
        ".hero h2{font-family:Georgia,serif;font-weight:400;font-size:26px;margin:4px 0;color:#0B1F3A}"
        ".hero p{margin:0;color:#4B5563;font-size:14px}"
        ".big{font-family:Georgia,serif;font-size:46px;color:#0B1F3A;font-weight:700}"
        "h3{font-family:Georgia,serif;font-weight:400;font-size:20px;color:#0B1F3A;margin:30px 0 10px;"
        "padding-bottom:6px;border-bottom:1px solid #D9D4C7}"
        "p{line-height:1.65;font-size:14.5px}"
        "table{width:100%;border-collapse:collapse}td{padding:7px 0;font-size:14px}"
        "td.n{width:42%}td.v{width:60px;text-align:right;font-weight:700;color:#0B1F3A}"
        ".bar{height:7px;background:#E7E3D8;border-radius:4px;overflow:hidden}"
        ".bar i{display:block;height:100%;background:#0B1F3A}"
        ".c{display:flex;gap:14px;align-items:flex-start;padding:14px 0;border-bottom:1px solid #EEE9DC}"
        ".cn{width:28px;height:28px;border-radius:50%;background:#0B1F3A;color:#F4E7C5;display:grid;"
        "place-items:center;font-weight:700;font-size:13px;flex:none}"
        ".ct{flex:1}.ct b{font-size:15.5px;color:#0B1F3A}.uni{display:block;color:#6B7280;font-size:12.5px;margin-top:2px}"
        ".ct p{margin:6px 0 8px;font-size:13.5px;color:#374151}.cv{font-family:Georgia,serif;font-size:22px;color:#0B1F3A;font-weight:700}"
        "ul,ol{padding-left:20px;line-height:1.7;font-size:14.5px}"
        ".foot{margin-top:30px;padding-top:14px;border-top:1px solid #D9D4C7;font-size:12px;color:#6B7280;line-height:1.6}"
        "@media print{body{background:#fff}.page{margin:0;box-shadow:none;max-width:none}}")
    return (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Reporte vocacional</title>"
        f"<style>{css}</style></head><body><div class='page'>"
        f"<div class='head'><div class='brand'>VOCACIONAL IA · UCV CHICLAYO</div><h1>Reporte vocacional</h1>"
        f"<p class='meta'>Estudiante: <b>{esc(nombre)}</b> &nbsp;·&nbsp; {hoy}</p></div><div class='body'>"
        f"<div class='hero'><div><div class='eyebrow'>MEJOR OPCIÓN</div><h2>{esc(top.get('nombre', '—'))}</h2>"
        f"<p>{esc(top.get('facultad') or top.get('universidad', ''))}</p></div>"
        f"<div class='big'>{pct(top.get('afinidad', 0))}%</div></div>"
        f"<h3>Síntesis del perfil</h3><p>{esc(p.get('resumen', ''))}</p>"
        f"<h3>Afinidad por área</h3><table>{filas_areas}</table>"
        f"<h3>Carreras recomendadas</h3>{lista_carreras}"
        f"<h3>Habilidades a reforzar</h3><ul>{lista('brechas')}</ul>"
        f"<h3>Plan de acción</h3><ol>{lista('plan')}</ol>"
        "<div class='foot'>Los porcentajes son relativos: comparan tus opciones entre sí para destacar cuál encaja mejor contigo. "
        "Este reporte es una orientación basada en tus respuestas y no reemplaza la atención de un psicólogo ni una decisión definitiva."
        "</div></div></div></body></html>")


# ---------------------------------- acceso ----------------------------------
st.markdown('<div class="hero"><h1>Vocacional IA</h1>'
            '<p>Descubre qué carrera de la Universidad César Vallejo, sede Chiclayo, encaja contigo.</p></div>',
            unsafe_allow_html=True)

if "usuario" not in st.session_state:
    tab_est, tab_adm = st.tabs(["🎓 Soy estudiante", "🛠️ Administrador"])
    with tab_est:
        st.caption("No necesitas crear cuenta: solo cuéntanos un poco sobre ti.")
        with st.form("ingreso"):
            nombre = st.text_input("Nombre y apellidos")
            c1, c2 = st.columns(2)
            edad = c1.number_input("Edad", min_value=10, max_value=25, value=16)
            sexo = c2.selectbox("Sexo", ["Masculino", "Femenino", "Prefiero no decirlo"])
            colegio = st.text_input("Colegio")
            grado = st.selectbox("Nivel", ["3ro de secundaria", "4to de secundaria", "5to de secundaria", "Egresado"], index=2)
            entrar = st.form_submit_button("Comenzar", type="primary")
        if entrar:
            u = api("POST", "/ingresar", json={"nombre": nombre, "edad": int(edad), "sexo": sexo,
                                               "colegio": colegio, "grado": grado})
            if u:
                st.session_state.usuario = u
                st.rerun()
    with tab_adm:
        with st.form("login_admin"):
            correo = st.text_input("Correo")
            clave = st.text_input("Contraseña", type="password")
            ok = st.form_submit_button("Entrar como administrador", type="primary")
        if ok:
            u = api("POST", "/login", json={"correo": correo, "contrasena": clave})
            if u and u.get("rol") == "Administrador":
                st.session_state.usuario = u
                st.rerun()
            elif u:
                st.error("Esta cuenta no tiene permisos de administrador.")
        with st.expander("Primera vez: crear cuenta de administrador"):
            st.caption("Solo funciona con los correos autorizados en ADMIN_EMAILS del archivo .env del backend.")
            with st.form("registro_admin"):
                n_a = st.text_input("Nombre")
                c_a = st.text_input("Correo", key="ra_correo")
                p_a = st.text_input("Contraseña (mínimo 6 caracteres)", type="password", key="ra_clave")
                crear = st.form_submit_button("Crear cuenta de administrador")
            if crear:
                u = api("POST", "/admin/registro", json={"nombre": n_a, "correo": c_a, "contrasena": p_a})
                if u:
                    st.session_state.usuario = u
                    st.rerun()
    st.stop()

usuario = st.session_state.usuario
es_admin = usuario.get("rol") == "Administrador"
uid = usuario["id_usuario"]

with st.sidebar:
    st.markdown(f'<div class="avatar">{esc(usuario["nombre"][:1].upper())}</div>', unsafe_allow_html=True)
    st.write(f"Hola, **{usuario['nombre']}**")
    st.caption("Administrador" if es_admin else "Estudiante")
    if st.button("Salir"):
        st.session_state.clear()
        st.rerun()


# ---------------------------------- evaluación interactiva ----------------------------------
def slider(q, escala, ev):
    return st.select_slider(q["texto"], options=[1, 2, 3, 4, 5], value=ev["resp"].get(q["id"], 3),
                            format_func=lambda x, e=escala: e[x], key=f"q_{q['id']}")


def pantalla_evaluacion():
    if "cuestionario" not in st.session_state:
        cu = api("GET", "/cuestionario")
        if not cu:
            return
        st.session_state.cuestionario = cu
    cu = st.session_state.cuestionario
    ev = st.session_state.setdefault("ev", {"fase": "intro", "pagina": 0, "resp": {}, "adapt": []})
    temas = cu["temas"]
    total = len(temas) + 1

    if ev["fase"] == "intro":
        n_base = sum(len(b["preguntas"]) for t in temas for b in t["bloques"])
        por_tema = n_base // len(temas)
        st.markdown(
            f'<div class="card"><div class="tag">Evaluación interactiva</div>'
            f'Recorrerás <b>{len(temas)} temas cortos</b> (salud, ingeniería, negocios y más), con '
            f'<b>{por_tema} preguntas</b> cada uno: unas sobre <b>lo que te atrae</b> y otras sobre '
            f'<b>lo que se te da bien</b>. Al final, el sistema se <b>adapta</b> a ti con 3 preguntas más '
            f'sobre tu área favorita. Toma unos 5 minutos. No hay respuestas buenas ni malas.</div>',
            unsafe_allow_html=True)
        fund = cu.get("fundamento", {})
        with st.expander("¿En qué se basa esta evaluación?"):
            st.write(fund.get("texto", ""))
            for r in fund.get("referencias", []):
                st.markdown(f"- {r}")
            st.caption(fund.get("estado", ""))
        if st.button("Comenzar evaluación", type="primary"):
            ev["fase"] = "test"
            st.rerun()
        return

    if ev["fase"] == "listo":
        st.success("¡Evaluación completada! Tu perfil ya está listo.")
        c1, c2 = st.columns(2)
        if c1.button("🎯 Ver mi perfil", type="primary"):
            st.session_state["_ir"] = "🎯 Mi perfil"
            st.rerun()
        if c2.button("🔄 Hacer otra evaluación"):
            st.session_state.pop("ev", None)
            st.rerun()
        return

    if ev["fase"] == "test":
        i = ev["pagina"]
        t = temas[i]
        st.progress(i / total, text=f"Tema {i + 1} de {len(temas)} · {t['titulo']}")
        st.markdown(f'<div class="tema" style="border-left:6px solid {t["color"]}"><h3>{esc(t["icono"])} {esc(t["titulo"])}</h3>'
                    f'<p>{esc(t["descripcion"])}</p></div>', unsafe_allow_html=True)
        with st.form(f"form_tema_{i}"):
            vals = {}
            for b in t["bloques"]:
                escala = {int(k): v for k, v in b["escala"].items()}
                st.markdown(f'<div class="bloque">{esc(b["titulo"])}</div>', unsafe_allow_html=True)
                for q in b["preguntas"]:
                    vals[q["id"]] = slider(q, escala, ev)
            c1, c2 = st.columns(2)
            atras = c1.form_submit_button("← Anterior")
            sig = c2.form_submit_button("Siguiente tema →", type="primary")
        if atras or sig:
            ev["resp"].update(vals)
            if atras:
                if i == 0:
                    ev["fase"] = "intro"
                else:
                    ev["pagina"] = i - 1
                st.rerun()
            elif i == len(temas) - 1:
                r = api("POST", "/cuestionario/adaptativas", json={"respuestas": ev["resp"]})
                if r:
                    ev["adapt"] = r["preguntas"]
                    ev["fase"] = "adaptativa"
                    st.rerun()
            else:
                ev["pagina"] = i + 1
                st.rerun()
        return

    if ev["fase"] == "adaptativa":
        st.progress((total - 1) / total, text="Últimas preguntas · Profundicemos")
        st.markdown("### Profundicemos en tu área favorita")
        st.caption("El sistema detectó el tema que más te atrae y quiere conocerte mejor en él.")
        escala = {int(k): v for k, v in cu["escala_adaptativa"].items()}
        with st.form("form_adapt"):
            vals = {}
            for q in ev["adapt"]:
                a = cu["areas"][q["area"]]
                st.markdown(f'<span class="areatag">{esc(a["icono"])} {esc(a["nombre"])}</span>', unsafe_allow_html=True)
                vals[q["id"]] = slider(q, escala, ev)
            c1, c2 = st.columns(2)
            atras = c1.form_submit_button("← Anterior")
            sig = c2.form_submit_button("Finalizar y ver mi perfil ✨", type="primary")
        if atras:
            ev["resp"].update(vals)
            ev["fase"] = "test"
            ev["pagina"] = len(temas) - 1
            st.rerun()
        if sig:
            ev["resp"].update(vals)
            ok = api("POST", "/evaluaciones", json={"id_usuario": uid, "respuestas": ev["resp"], "nivel_adaptativo": 2})
            if ok:
                with st.spinner("Analizando tus respuestas con IA..."):
                    res = api("POST", f"/generar-perfil/{uid}")
                if res:
                    st.session_state.perfil = res["perfil"]
                    ev["fase"] = "listo"
                    st.session_state["_ir"] = "🎯 Mi perfil"
                    st.rerun()


# ---------------------------------- perfil vocacional ----------------------------------
def pantalla_perfil():
    p = st.session_state.get("perfil")
    if not p:
        try:
            r = requests.get(f"{API}/perfil/{uid}", timeout=30)
            p = r.json().get("perfil") if r.status_code == 200 else None
        except (requests.RequestException, ValueError):
            p = None
    if not p:
        st.info("Aún no tienes un perfil. Completa la evaluación para generarlo.")
        return
    if p.get("modo") == "respaldo":
        st.info("Este resultado se calculó con tus respuestas porque el servicio de IA está saturado. "
                "Vuelve a intentarlo más tarde para el análisis completo con Gemini.")

    catalogo = {c["nombre"].strip().lower(): c for c in (api("GET", "/carreras") or [])}
    for c in p.get("carreras", []):  # enlaces de malla y mercado laboral siempre actualizados
        m = catalogo.get(str(c.get("nombre", "")).strip().lower())
        if m:
            c.update({"url_malla": m["url_malla"], "malla_directa": m["malla_directa"], "facultad": m["facultad"],
                      "demanda_laboral": m["demanda_laboral"], "salario_promedio": m["salario_promedio"],
                      "sectores_clave": m["sectores_clave"]})

    st.markdown(f'<div class="card quote"><div class="tag">Síntesis de tu perfil</div>{esc(p.get("resumen", ""))}</div>',
                unsafe_allow_html=True)
    if p.get("fortalezas"):
        st.markdown("".join(f'<span class="pill ok">💪 {esc(f)}</span>' for f in p["fortalezas"]), unsafe_allow_html=True)

    areas = p.get("areas") or []
    if areas:
        c1, c2 = st.columns([1.1, 1])
        c1.markdown(f'<div class="card"><div class="tag">Mapa de tus intereses</div>{radar_svg(areas)}</div>',
                    unsafe_allow_html=True)
        c2.markdown(f'<div class="card"><div class="tag">Afinidad por área</div>{barras_areas(areas)}</div>',
                    unsafe_allow_html=True)

    carreras = p.get("carreras") or []
    if carreras:
        c0 = carreras[0]
        a0 = pct(c0.get("afinidad"))
        st.markdown(
            f'<div class="top"><div class="ring" style="background:conic-gradient(#fff {a0}%, rgba(255,255,255,.3) 0)">'
            f'<span>{a0}%</span></div><div><div class="mini">Tu mejor opción</div><h2>{esc(c0.get("nombre"))}</h2>'
            f'<div>{esc(c0.get("facultad") or c0.get("universidad"))}</div>'
            f'<div style="margin-top:6px;opacity:.95">{esc(c0.get("motivo"))}</div>'
            f'<div>{chips_mercado(c0)}</div>{boton_malla(c0, claro=True)}</div></div>', unsafe_allow_html=True)
        st.caption("Los porcentajes son relativos: comparan tus opciones entre sí para destacar cuál encaja mejor contigo.")
        if len(carreras) > 1:
            st.markdown("### Otras carreras que encajan contigo")
            for i, c in enumerate(carreras[1:], start=1):
                a = pct(c.get("afinidad"))
                color = COLORES[i % len(COLORES)]
                st.markdown(
                    f'<div class="card"><div class="row" style="margin-top:0"><b>{esc(c.get("nombre"))}</b>'
                    f'<span class="pct" style="color:{color}">{a}%</span></div>'
                    f'<div class="sub">{esc(c.get("facultad") or c.get("universidad"))}</div>'
                    f'<div class="bar"><div style="width:{a}%;background:{color}"></div></div>'
                    f'<div class="why2">{esc(c.get("motivo"))}</div>{chips_mercado(c)}<div>{boton_malla(c)}</div></div>',
                    unsafe_allow_html=True)

    if p.get("brechas"):
        st.markdown("### Brechas de competencias")
        st.markdown("".join(f'<span class="pill">🎯 {esc(b)}</span>' for b in p["brechas"]), unsafe_allow_html=True)
    if p.get("plan"):
        st.markdown("### Tu plan de acción")
        st.markdown("".join(f'<div class="step"><div class="n">{i}</div><div>{esc(s)}</div></div>'
                            for i, s in enumerate(p["plan"], start=1)), unsafe_allow_html=True)

    st.markdown('<div class="reporte"><div class="r-tag">REPORTE</div><h3>Lleva tu resultado contigo</h3>'
                '<p>Descarga un reporte con tu síntesis, las carreras recomendadas y tu plan de acción. '
                'Ábrelo en el navegador y guárdalo como PDF con Ctrl + P.</p></div>', unsafe_allow_html=True)
    st.download_button("Descargar reporte vocacional", data=reporte_html(p, usuario["nombre"]),
                       file_name="reporte_vocacional.html", mime="text/html")

    st.markdown("### ¿Qué te pareció?")
    with st.form("feedback"):
        nivel = st.select_slider("¿Qué tan útil fue tu resultado?", options=[1, 2, 3, 4, 5], value=4,
                                 format_func=lambda x: "⭐" * x)
        com = st.text_area("Comentarios (opcional)")
        if st.form_submit_button("Enviar opinión"):
            if api("POST", "/retroalimentacion", json={"id_usuario": uid, "nivel_satisfaccion": nivel, "comentarios": com}):
                st.success("¡Gracias por tu opinión!")


# ---------------------------------- oferta educativa ----------------------------------
def pantalla_oferta():
    carreras = api("GET", "/carreras") or []
    if not carreras:
        st.info("Todavía no hay carreras cargadas. Revisa la terminal del backend.")
        return
    recomendadas = {c["nombre"].lower() for c in (st.session_state.get("perfil") or {}).get("carreras", [])}
    st.markdown(f'<div class="card"><div class="tag">Carreras de la UCV · Sede Chiclayo</div>'
                f'{len(carreras)} carreras de pregrado en 4 facultades. Abre cada una para ver su malla curricular '
                f'y los datos del mercado laboral.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    filtro = c1.selectbox("Facultad", ["Todas"] + FACULTADES)
    busca = c2.text_input("Buscar carrera").strip().lower()
    mostradas = 0
    for fac in FACULTADES + sorted({c["facultad"] for c in carreras} - set(FACULTADES)):
        grupo = [c for c in carreras if c["facultad"] == fac
                 and (filtro == "Todas" or filtro == fac) and (not busca or busca in c["nombre"].lower())]
        if not grupo:
            continue
        st.markdown(f"### {fac}")
        for c in grupo:
            mostradas += 1
            estrella = "⭐ " if c["nombre"].lower() in recomendadas else ""
            with st.expander(f"{estrella}{c['icono']} {c['nombre']}"):
                datos = ""
                if c.get("tipo"):
                    datos += f'<span class="chip">🏷️ {esc(c["tipo"])}</span>'
                if c.get("alcance"):
                    datos += f'<span class="chip">🌎 {esc(c["alcance"])}</span>'
                if c.get("area_nombre"):
                    datos += f'<span class="chip">{esc(c["icono"])} {esc(c["area_nombre"])}</span>'
                st.markdown(datos + chips_mercado(c) + f"<div>{boton_malla(c)}</div>", unsafe_allow_html=True)
                if c.get("malla"):
                    st.markdown("**Resumen de la malla**")
                    for linea in c["malla"].split("\n"):
                        if linea.strip():
                            st.markdown(f"- {linea.strip()}")
                if not c.get("malla_directa"):
                    st.caption("Aún no se cargó el enlace directo de la malla de esta carrera; el botón abre la página oficial de carreras de la UCV.")
    if not mostradas:
        st.info("No hay carreras que coincidan con tu búsqueda.")


# ---------------------------------- dashboard ----------------------------------
def pantalla_dashboard():
    h = api("GET", f"/historial/{uid}") or []
    if not h:
        st.info("Aún no tienes evaluaciones. Completa una para ver tu dashboard.")
        return
    ult = h[0]["perfil"]
    mejor_area = ult["areas"][0] if ult.get("areas") else None
    mejor_carrera = (ult.get("carreras") or [{}])[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Evaluaciones", len(h))
    c2.metric("Área principal", f"{mejor_area['icono']} {CORTO.get(mejor_area['clave'], '')}" if mejor_area else "—")
    c3.metric("Mejor carrera", mejor_carrera.get("nombre", "—"))

    st.markdown("### Tu evolución")
    if len(h) >= 2:
        filas = []
        for it in reversed(h):
            fila = {"Fecha": it["fecha"][:16].replace("T", " ")}
            for a in it["perfil"].get("areas", []):
                fila[CORTO.get(a["clave"], a["nombre"])] = a["puntaje"]
            filas.append(fila)
        st.line_chart(pd.DataFrame(filas).set_index("Fecha"))
    else:
        df = pd.DataFrame({"Afinidad (%)": [a["puntaje"] for a in ult["areas"]]},
                          index=[CORTO.get(a["clave"], a["nombre"]) for a in ult["areas"]])
        st.bar_chart(df, color="#F59E0B")
        st.caption("Haz otra evaluación más adelante para ver cómo cambian tus intereses.")

    st.markdown("### Historial de evaluaciones")
    for it in h:
        p = it["perfil"]
        top = (p.get("carreras") or [{}])[0]
        titulo = f"{it['fecha'][:16].replace('T', ' ')} · {top.get('nombre', 'Sin carrera')} ({pct(top.get('afinidad'))}%)"
        with st.expander(titulo):
            st.markdown(f'<div class="card" style="margin:0">{barras_areas(p.get("areas", []))}</div>', unsafe_allow_html=True)
            st.caption(p.get("resumen", ""))


# ---------------------------------- administrador ----------------------------------
def guardar_carrera(c, **cambios):
    datos = {"id_admin": uid, "nombre": c["nombre"], "facultad": c.get("facultad"),
             "area_conocimiento": c.get("area_conocimiento"), "tipo": c.get("tipo"), "alcance": c.get("alcance"),
             "malla": c.get("malla"), "malla_url": c.get("malla_url"),
             "demanda_laboral": c.get("demanda_laboral"), "salario_promedio": c.get("salario_promedio"),
             "sectores_clave": c.get("sectores_clave")}
    datos.update(cambios)
    return api("PUT", f"/admin/carreras/{c['id']}", json=datos)


def pantalla_admin():
    carreras = api("GET", "/carreras") or []
    if not carreras:
        st.info("No hay carreras en la base de datos.")
        return
    st.markdown('<div class="card"><div class="tag">Base de conocimiento</div>'
                'Actualiza los datos de las carreras de la UCV: el enlace de la malla curricular y el mercado '
                'laboral. Los cambios se ven al instante en la oferta educativa y en las recomendaciones.</div>',
                unsafe_allow_html=True)
    opciones = {f"{c['nombre']} · {c['facultad'].replace('Facultad de ', '')}": c for c in carreras}
    c = opciones[st.selectbox("Selecciona una carrera", list(opciones))]
    t1, t2 = st.tabs(["📚 Datos y malla", "💼 Mercado laboral"])
    alcances = ["", "Local", "Regional", "Nacional", "Internacional"]
    with t1:
        with st.form(f"f_carrera_{c['id']}"):
            nombre = st.text_input("Nombre", c["nombre"])
            fac = st.selectbox("Facultad", FACULTADES,
                               index=FACULTADES.index(c["facultad"]) if c.get("facultad") in FACULTADES else 0)
            tipo = st.text_input("Tipo", c.get("tipo") or "Pregrado")
            alc = st.selectbox("Alcance", alcances, index=alcances.index(c["alcance"]) if c.get("alcance") in alcances else 0)
            url = st.text_input("Enlace de la malla curricular (UCV Chiclayo)", c.get("malla_url") or "",
                                placeholder="https://...")
            malla = st.text_area("Resumen de la malla (opcional, un ciclo o curso por línea)", c.get("malla") or "", height=160)
            if st.form_submit_button("Guardar datos", type="primary"):
                if guardar_carrera(c, nombre=nombre, facultad=fac, tipo=tipo, alcance=alc, malla_url=url, malla=malla):
                    st.success("Carrera actualizada.")
    with t2:
        with st.form(f"f_mercado_{c['id']}"):
            dem = ["", "Alta", "Media", "Baja"]
            demanda = st.selectbox("Demanda laboral", dem, index=dem.index(c["demanda_laboral"]) if c.get("demanda_laboral") in dem else 0)
            sueldo = st.number_input("Salario promedio mensual (S/)", min_value=0.0, step=100.0, value=float(c.get("salario_promedio") or 0))
            sectores = st.text_area("Sectores clave", c.get("sectores_clave") or "")
            if st.form_submit_button("Guardar mercado laboral", type="primary"):
                if guardar_carrera(c, demanda_laboral=demanda, salario_promedio=sueldo or None, sectores_clave=sectores):
                    st.success("Mercado laboral actualizado.")


# ---------------------------------- reportes del administrador ----------------------------------
def pantalla_reportes():
    datos = api("GET", f"/admin/reportes?id_admin={uid}")
    if not datos:
        return
    r, evs, ops = datos["resumen"], datos["evaluaciones"], datos["opiniones"]
    st.markdown('<div class="reporte"><div class="r-tag">PANEL DEL ADMINISTRADOR</div><h3>Reportes de la plataforma</h3>'
                '<p>Resumen de las evaluaciones realizadas, reportes individuales y opiniones de los estudiantes. '
                'Contiene datos personales: úsalo con cuidado.</p></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Estudiantes", r["estudiantes"])
    c2.metric("Evaluaciones", r["evaluaciones"])
    c3.metric("Satisfacción", f"{r['satisfaccion']} ⭐" if r["satisfaccion"] else "—")
    c4.metric("Análisis con IA", f"{r['con_ia']}/{r['evaluaciones']}")
    if not evs:
        st.info("Todavía no hay evaluaciones completadas.")
        return

    st.markdown("### Áreas principales de los estudiantes")
    st.bar_chart(pd.DataFrame({"Estudiantes": list(r["areas"].values())}, index=list(r["areas"].keys())), color="#C9A227")
    st.markdown("### Carreras más recomendadas")
    st.bar_chart(pd.DataFrame({"Veces": list(r["carreras"].values())}, index=list(r["carreras"].keys())), color="#1E3A6E")

    st.markdown("### Evaluaciones realizadas")
    tabla = pd.DataFrame([{
        "Fecha": e["fecha"][:16].replace("T", " "), "Estudiante": e["nombre"], "Edad": e["edad"], "Sexo": e["sexo"],
        "Colegio": e["colegio"], "Nivel": e["grado"], "Área principal": e["area_principal"],
        "Carrera principal": e["carrera_principal"], "Afinidad (%)": e["afinidad"],
        "Análisis": "IA" if e["modo"] == "ia" else "Respaldo"} for e in evs])
    st.dataframe(tabla, hide_index=True)
    st.download_button("Exportar tabla (CSV)", data=tabla.to_csv(index=False).encode("utf-8-sig"),
                       file_name="evaluaciones_vocacional_ia.csv", mime="text/csv")

    st.markdown("### Reporte de un estudiante")
    opciones_ev = {f"{e['nombre']} · {e['fecha'][:16].replace('T', ' ')}": e["id_evaluacion"] for e in evs}
    elegido = st.selectbox("Selecciona una evaluación", list(opciones_ev))
    det = api("GET", f"/admin/reportes/{opciones_ev[elegido]}?id_admin={uid}")
    if det:
        p = det["perfil"]
        st.markdown(f'<div class="card quote"><div class="tag">{esc(det["nombre"])}</div>{esc(p.get("resumen", ""))}</div>',
                    unsafe_allow_html=True)
        areas = p.get("areas") or []
        if areas:
            g1, g2 = st.columns([1.1, 1])
            g1.markdown(f'<div class="card"><div class="tag">Mapa de intereses</div>{radar_svg(areas)}</div>', unsafe_allow_html=True)
            g2.markdown(f'<div class="card"><div class="tag">Afinidad por área</div>{barras_areas(areas)}</div>', unsafe_allow_html=True)
        for c in p.get("carreras", []):
            st.markdown(f'<div class="card"><div class="row" style="margin-top:0"><b>{esc(c.get("nombre"))}</b>'
                        f'<span class="pct">{pct(c.get("afinidad"))}%</span></div>'
                        f'<div class="why2">{esc(c.get("motivo"))}</div></div>', unsafe_allow_html=True)
        archivo = re.sub(r"[^A-Za-z0-9_-]+", "_", det["nombre"]).strip("_") or "estudiante"
        st.download_button("Descargar reporte de este estudiante", data=reporte_html(p, det["nombre"]),
                           file_name=f"reporte_{archivo}.html", mime="text/html")

    with st.expander(f"Opiniones de los estudiantes ({r['opiniones']})"):
        if not ops:
            st.caption("Aún no hay opiniones.")
        for o in ops:
            st.markdown(f"**{'⭐' * (o['nivel_satisfaccion'] or 0)}** · {esc(o.get('nombre') or 'Anónimo')} · "
                        f"{o['fecha'][:10]}  \n{esc(o.get('comentarios') or '_Sin comentario_')}")


# ---------------------------------- navegación ----------------------------------
opciones = ["📝 Evaluación", "🎯 Mi perfil", "🏫 Oferta educativa", "📈 Mi dashboard"]
if es_admin:
    opciones += ["📊 Reportes", "🛠️ Base de conocimiento"]
if "_ir" in st.session_state:
    st.session_state["nav"] = st.session_state.pop("_ir")
vista = st.radio("Navegación", opciones, horizontal=True, key="nav", label_visibility="collapsed")
st.divider()

if vista.startswith("📝"):
    pantalla_evaluacion()
elif vista.startswith("🎯"):
    pantalla_perfil()
elif vista.startswith("🏫"):
    pantalla_oferta()
elif vista.startswith("📈"):
    pantalla_dashboard()
elif vista.startswith("📊"):
    pantalla_reportes()
else:
    pantalla_admin()