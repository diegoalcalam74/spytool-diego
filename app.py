import streamlit as st
import google.generativeai as genai
from apify_client import ApifyClient
import urllib.parse
from datetime import datetime, date
from docx import Document
from io import BytesIO
import time
from PIL import Image, ImageDraw, ImageFont
import requests
from gtts import gTTS
from google.api_core.exceptions import ResourceExhausted, NotFound
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="SpyTool Pro: Global Edition 🌎", layout="wide")

# --- GESTIÓN DE SECRETOS (AUTOMÁTICA) ---
# Intenta buscar las claves en la caja fuerte (Secrets)
api_key_google = st.secrets.get("GOOGLE_API_KEY", None)
api_key_apify = st.secrets.get("APIFY_API_TOKEN", None)

# --- BLINDAJE ---
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- FUNCIONES ---
def crear_word(titulo_libro, capitulos_guardados):
    doc = Document()
    doc.add_heading(titulo_libro, 0)
    for cap in capitulos_guardados:
        doc.add_heading(cap['titulo'], level=1)
        doc.add_paragraph(cap['contenido'])
        doc.add_page_break()
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def crear_markdown(titulo_libro, capitulos_guardados):
    texto_completo = f"# {titulo_libro}\n\n"
    for cap in capitulos_guardados:
        texto_completo += f"## {cap['titulo']}\n\n"
        texto_completo += f"{cap['contenido']}\n\n"
        texto_completo += "---\n\n"
    return texto_completo

def texto_a_audio(texto, idioma='es'):
    try:
        tts = gTTS(text=texto, lang=idioma, slow=False)
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer
    except: return None

def consultar_gemini_robusto(prompt, api_key, model_name_principal, lista_modelos_disponibles, stream=False):
    if not api_key: return None
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(model_name_principal)
        if stream: return model.generate_content(prompt, stream=True, safety_settings=SAFETY_SETTINGS)
        else: return model.generate_content(prompt, safety_settings=SAFETY_SETTINGS).text
    except (ResourceExhausted, NotFound):
        st.toast(f"⚠️ Motor {model_name_principal} ocupado. Buscando respaldo...", icon="🔄")
        time.sleep(1) 
        for backup_name in lista_modelos_disponibles:
            if backup_name != model_name_principal:
                try:
                    model_backup = genai.GenerativeModel(backup_name)
                    if stream: return model_backup.generate_content(prompt, stream=True, safety_settings=SAFETY_SETTINGS)
                    else: return model_backup.generate_content(prompt, safety_settings=SAFETY_SETTINGS).text
                except: continue
        st.error("🚦 Tráfico extremo. Espera 1 min.")
        return None
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return None

# --- ESTADO ---
if 'borrador_libro' not in st.session_state: st.session_state['borrador_libro'] = []
if 'mis_modelos' not in st.session_state: st.session_state['mis_modelos'] = []

# --- BARRA LATERAL (AUTOMATIZADA) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    if not api_key_google:
        api_key_google = st.text_input("1. Google API Key:", type="password")
        st.warning("⚠️ Clave no detectada en Secrets. Úsala manual.")
    else:
        st.success("✅ Google Key: Conectada (Secrets)")
        
    modelo_seleccionado = "models/gemini-1.5-flash" 
    
    if api_key_google:
        try:
            genai.configure(api_key=api_key_google)
            try:
                lista_reales = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        lista_reales.append(m.name)
                st.session_state['mis_modelos'] = lista_reales
            except:
                lista_reales = ["models/gemini-1.5-flash", "models/gemini-pro"]

            if lista_reales:
                index_defecto = 0
                for i, nombre in enumerate(lista_reales):
                    if "gemini-1.5-flash" in nombre: index_defecto = i
                modelo_seleccionado = st.selectbox("🤖 Motor Principal:", lista_reales, index=index_defecto)
        except: pass
    
    st.divider()
    
    if not api_key_apify:
        api_key_apify = st.text_input("2. Apify Token (Opcional):", type="password")
    else:
        st.success("✅ Apify Token: Conectado (Secrets)")
        
    st.divider()
    if len(st.session_state['borrador_libro']) > 0:
        if st.button("🗑️ Reiniciar Libro"):
            st.session_state['borrador_libro'] = []
            st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("🏰 SpyTool Pro: Global Edition 🌎")

if not api_key_google:
    st.info("👋 ¡Hola! Para empezar, configura tus llaves en los 'Secrets' de Streamlit o ingrésalas en la barra lateral.")
    st.stop()

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📡 Radar", "🏭 Fábrica", "🎨 Portada Pro", "📢 Marketing", "🌐 Landing Page", "🎧 Extras", "🌪️ Embudo"])

# PESTAÑA 1: RADAR (AHORA CON BRASIL)
with tab1:
    st.header("Investigación")
    modo = st.radio("Modo:", ["🤖 Automático", "✍️ Manual"], horizontal=True)
    if modo == "🤖 Automático":
        c1, c2 = st.columns(2)
        with c1: keyword = st.text_input("Nicho:", value="Yoga")
        with c2: 
            # ¡AQUÍ ESTÁ BRASIL AGREGADO!
            pais = st.selectbox("País:", ["US", "ES", "MX", "BR"]) 
        if st.button("🚀 Buscar"):
            if not api_key_apify: st.error("Falta Token Apify.")
            else:
                try:
                    client = ApifyClient(api_key_apify)
                    encoded = urllib.parse.quote(keyword)
                    run_input = { "startUrls": [{ "url": f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={pais}&q={encoded}&search_type=keyword_unordered&media_type=all" }], "maxItems": 3 }
                    with st.spinner("Buscando..."):
                        run = client.actor("apify/facebook-ads-scraper").call(run_input=run_input, timeout_secs=60)
                    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
                    st.success(f"{len(items)} anuncios.")
                    for i, item in enumerate(items):
                        txt = item.get('adBody') or item.get('primaryText') or ""
                        with st.container(border=True):
                            st.text_area("Copy", txt, height=60, key=f"t{i}")
                            if st.button("🧠 Usar Tema", key=f"b{i}"):
                                st.session_state['tema'] = txt[:800]
                                st.success("Tema cargado.")
                except Exception as e: st.error(f"Error: {e}")
    else:
        tm = st.text_area("Pega anuncio:")
        if st.button("Analizar"):
            st.session_state['tema'] = tm[:800]
            st.success("Tema cargado.")

# PESTAÑA 2: FÁBRICA
with tab2:
    st.header("🏭 Escritura")
    tema = st.session_state.get('tema', 'Sin tema.')
    st.caption(f"Tema: {tema[:50]}...")
    c_m, c_w = st.columns(2)
    with c_m:
        if st.button("Generar Índice"):
            res = consultar_gemini_robusto(f"Crea índice ebook: {tema}", api_key_google, modelo_seleccionado, st.session_state['mis_modelos'])
            if res: st.session_state['mapa'] = res
        if 'mapa' in st.session_state: st.markdown(st.session_state['mapa'])
    with c_w:
        tit_cap = st.text_input("Título Cap:")
        inst = st.text_area("Instrucciones:")
        if st.button("Escribir"):
            prompt = f"Escribe cap '{tit_cap}'. Inst: {inst}. Tema: {tema}. Markdown."
            cont = st.empty()
            full = ""
            res = consultar_gemini_robusto(prompt, api_key_google, modelo_seleccionado, st.session_state['mis_modelos'], stream=True)
            if res:
                for ch in res:
                    try: 
                        if ch.text: full += ch.text; cont.markdown(full + "▌")
                    except: pass
                cont.markdown(full)
                st.session_state['temp_cap'] = full; st.session_state['temp_tit'] = tit_cap
        if 'temp_cap' in st.session_state:
            if st.button("💾 Guardar Cap"):
                st.session_state['borrador_libro'].append({"titulo":st.session_state['temp_tit'], "contenido":st.session_state['temp_cap']})
                st.success("Guardado.")
                del st.session_state['temp_cap']
                st.rerun()
    if len(st.session_state['borrador_libro']) > 0:
        st.download_button("Descargar Libro", crear_word("Libro", st.session_state['borrador_libro']), "Libro.docx")

# PESTAÑA 3: PORTADA PRO
with tab3:
    st.header("🎨 Ingeniero de Portadas (Ideogram)")
    t_l = st.text_input("Título Libro:", placeholder="DOMINA TU MENTE")
    st_l = st.selectbox("Estilo:", ["Cinemática 3D", "Grabado de Lujo", "Neón Cyberpunk", "Minimalista Editorial"])
    if st.button("🧠 Crear Prompt Maestro"):
        with st.spinner("Creando prompt..."):
            prompt_base = f"Actúa como Prompt Engineer para Ideogram AI. Libro: '{st.session_state.get('tema','')}'. Título: '{t_l}'. Estilo: {st_l}. Escribe un prompt en INGLÉS detallado para generar la portada con el texto integrado realista."
            res = consultar_gemini_robusto(prompt_base, api_key_google, modelo_seleccionado, st.session_state['mis_modelos'])
            if res: st.code(res, language="text"); st.success("Copia y pega en Ideogram.ai")

# PESTAÑA 4: MARKETING
with tab4:
    st.header("📢 Marketing Suite")
    tema_marketing = st.session_state.get('tema', 'Sin tema')
    tab_copy, tab_visual = st.tabs(["✍️ Copywriting", "🎨 Creativos Visuales"])
    with tab_copy:
        if st.button("Generar Copies"):
            prompt = f"Escribe 3 anuncios Facebook Ads para libro sobre {tema_marketing}. Incluye emojis y CTA. Tono persuasivo."
            res = consultar_gemini_robusto(prompt, api_key_google, modelo_seleccionado, st.session_state['mis_modelos'])
            if res: st.markdown(res)
    with tab_visual:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            estilo_ads = st.selectbox("Estilo Imagen Ads:", ["Ilustración Metafórica", "Foto Stock", "UGC"])
            if st.button("Generar Prompts Visuales"):
                p = f"3 prompts visuales (Inglés) para Ads de '{tema_marketing}'. Estilo {estilo_ads}. CUMPLE NORMAS FACEBOOK."
                res = consultar_gemini_robusto(p, api_key_google, modelo_seleccionado, st.session_state['mis_modelos'])
                if res: st.markdown(res)
        with col_v2:
            if st.button("Escribir Guiones Reels"):
                p = f"3 Guiones Reels 15s para '{tema_marketing}'. Tabla: Tiempo | Visual | Audio. Gancho fuerte."
                res = consultar_gemini_robusto(p, api_key_google, modelo_seleccionado, st.session_state['mis_modelos'])
                if res: st.markdown(res)

# PESTAÑA 5: LANDING PAGE
with tab5:
    st.header("🌐 Landing Page")
    prod = st.text_input("Producto:", value="Mi Ebook")
    prec = st.text_input("Precio:", value="$17")
    if st.button("🏗️ Construir Web"):
        prompt_web = f"HTML5 landing page moderna para '{prod}' ({st.session_state.get('tema','')}). Precio {prec}. Con CSS. Bonita, responsive. Solo código HTML puro."
        res = consultar_gemini_robusto(prompt_web, api_key_google, modelo_seleccionado, st.session_state['mis_modelos'])
        if res:
            clean = res.replace("```html","").replace("```","")
            st.download_button("Descargar HTML", clean, "landing.html")
            st.components.v1.html(clean, height=400, scrolling=True)

# PESTAÑA 6: EXTRAS
with tab6:
    st.header("🎧 Extras & Legales")
    col_a, col_l = st.columns(2)
    with col_a:
        st.subheader("Audiobook")
        if len(st.session_state['borrador_libro']) > 0:
            titulos = [c['titulo'] for c in st.session_state['borrador_libro']]
            sel = st.selectbox("Capítulo:", titulos)
            cont_cap = next((c['contenido'] for c in st.session_state['borrador_libro'] if c['titulo'] == sel), "")
            if st.button("Convertir a MP3"):
                with st.spinner("Grabando..."):
                    ab = texto_a_audio(cont_cap)
                    if ab: st.audio(ab); st.download_button("Descargar MP3", ab, f"{sel}.mp3")
    with col_l:
        st.subheader("Textos Legales")
        emp = st.text_input("Empresa:")
        mail = st.text_input("Email:")
        if st.button("Generar Legales"):
            p = f"Textos legales HTML (Privacidad, Descargo Responsabilidad, Términos) para {emp} ({mail})."
            res = consultar_gemini_robusto(p, api_key_google, modelo_seleccionado, st.session_state['mis_modelos'])
            if res: st.markdown(res)

# PESTAÑA 7: EMBUDOS
with tab7:
    st.header("🌪️ Arquitecto de Embudos")
    tema_funnel = st.session_state.get('tema', 'Sin tema')
    col_bump, col_upsell = st.columns(2)
    with col_bump:
        st.subheader("Order Bump")
        tipo_bump = st.selectbox("Tipo:", ["Audiobook", "Checklist", "Plantilla"])
        if st.button("Redactar Bump"):
            p = f"Texto Order Bump para '{tema_funnel}'. Producto: {tipo_bump}. Título, Beneficio, Descuento."
            res = consultar_gemini_robusto(p, api_key_google, modelo_seleccionado, st.session_state['mis_modelos'])
            if res: st.info(res)
    with col_upsell:
        st.subheader("Upsell")
        tipo_upsell = st.selectbox("Tipo:", ["Masterclass", "Pack 5 Ebooks", "VIP"])
        if st.button("Guion Upsell"):
            p = f"Guion VSL Upsell para '{tema_funnel}'. Oferta: {tipo_upsell}. Estructura: Felicitar -> Problema -> Solución -> Escasez."
            res = consultar_gemini_robusto(p, api_key_google, modelo_seleccionado, st.session_state['mis_modelos'])
            if res: st.markdown(res)
