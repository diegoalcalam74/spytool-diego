import streamlit as st
import google.generativeai as genai
from apify_client import ApifyClient
import json
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SpyTool V9.2 Full Equipo", page_icon="🏎️", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; transition: all 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .header-style { font-size: 24px; font-weight: bold; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #f0f2f6; }
    .success-box { padding: 15px; background-color: #d4edda; color: #155724; border-radius: 8px; border: 1px solid #c3e6cb; margin-bottom: 15px; }
    .warning-box { padding: 15px; background-color: #fff3cd; color: #856404; border-radius: 8px; border: 1px solid #ffeeba; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN INTELIGENTE: AUTO-DETECTAR MODELO (LA CURA DEL ZOMBI) ---
def conseguir_modelo_valido(api_key):
    if not api_key: return None
    genai.configure(api_key=api_key)
    try:
        # Preguntar a Google qué modelos tiene disponibles
        mis_modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Prioridad de modelos (Del más rápido al más robusto)
        if "models/gemini-1.5-flash" in mis_modelos: return "gemini-1.5-flash"
        if "models/gemini-1.5-pro" in mis_modelos: return "gemini-1.5-pro"
        if "models/gemini-pro" in mis_modelos: return "gemini-pro"
        
        # Si no encuentra favoritos, devuelve el primero que haya
        return mis_modelos[0].replace("models/", "") if mis_modelos else None
    except:
        return None

# --- BARRA LATERAL (PANEL DE CONTROL) ---
with st.sidebar:
    st.title("SpyTool V9.2 🏎️")
    st.markdown("---")
    
    # GESTIÓN DE CLAVES
    api_key_google = st.secrets.get("GOOGLE_API_KEY")
    api_token_apify = st.secrets.get("APIFY_API_TOKEN")

    if not api_key_google:
        api_key_google = st.text_input("Google API Key:", type="password")
    
    if not api_token_apify:
        api_token_apify = st.text_input("Apify Token:", type="password")
    
    st.markdown("---")
    
    # AUTO-DETECCIÓN DE MOTOR
    modelo_actual = "gemini-pro" # Fallback por seguridad
    if api_key_google:
        detectado = conseguir_modelo_valido(api_key_google)
        if detectado:
            modelo_actual = detectado
            st.success(f"🧠 Motor Activo: **{modelo_actual}**")
        else:
            st.error("❌ API Key inválida")
    else:
        st.warning("⚠️ Esperando Llaves...")

# --- FUNCIÓN GENERADORA ---
def consultar_gemini(prompt, api_key, modelo):
    if not api_key: return "⚠️ Error: Falta la Google API Key."
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(modelo)
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Error del Motor: {str(e)}"

# --- ESTADO DE LA SESIÓN (MEMORIA) ---
if 'tema' not in st.session_state: st.session_state['tema'] = ""
if 'publico' not in st.session_state: st.session_state['publico'] = ""
if 'indice' not in st.session_state: st.session_state['indice'] = ""
if 'resultados_radar' not in st.session_state: st.session_state['resultados_radar'] = []

# --- TABS PRINCIPALES ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🕵️ Radar", "🏭 Fábrica", "🎨 Portada", "📢 Marketing", "🌐 Landing", "💰 Monetización"
])

# ================= TAB 1: RADAR (INVESTIGACIÓN) =================
with tab1:
    st.markdown('<div class="header-style">🕵️ Radar de Mercado</div>', unsafe_allow_html=True)
    modo = st.radio("Modo de Espionaje:", ["🤖 Automático (Apify)", "✍️ Manual (Pegar Texto)"], horizontal=True)
    
    if modo == "🤖 Automático (Apify)":
        col1, col2 = st.columns(2)
        with col1: keyword = st.text_input("Nicho / Palabra Clave:", placeholder="Ej: Yoga para espalda")
        with col2: pais = st.selectbox("País Objetivo:", ["BR", "US", "ES", "MX", "CO"])
        
        if st.button("🚀 Escanear Facebook Ads"):
            if not api_token_apify: st.error("Falta Token de Apify en la barra lateral.")
            else:
                with st.status("Hackeando la Matrix (Escaneando Ads)...") as status:
                    try:
                        client = ApifyClient(api_token_apify)
                        run = client.actor("curious_coder/facebook-ads-library-scraper").call(run_input={"queries": [keyword], "countryCode": pais, "maxResults": 3})
                        res = [item.get("content", "") for item in client.dataset(run["defaultDatasetId"]).iterate_items() if item.get("content")]
                        
                        if res:
                            st.session_state['resultados_radar'] = res
                            status.update(label="¡Datos Encontrados!", state="complete")
                            st.success(f"Se encontraron {len(res)} anuncios ganadores.")
                        else:
                            status.update(label="No se encontraron datos.", state="error")
                            st.warning("No hay anuncios recientes para esta búsqueda.")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
        
        if st.session_state['resultados_radar']:
            if st.button("🧠 Analizar Datos con IA"):
                txt = "\n".join(st.session_state['resultados_radar'][:3])
                p = f"Analiza estos anuncios de '{keyword}':\n{txt}\n\nDime:\n1. Cuál es el dolor principal.\n2. Cuál es la promesa.\n3. Define el Avatar exacto.\nResponde en formato JSON: {{'dolor': '', 'promesa': '', 'avatar': ''}}"
                res = consultar_gemini(p, api_key_google, modelo_actual)
                try:
                    d = json.loads(res.replace("```json","").replace("```",""))
                    st.session_state['tema'] = keyword
                    st.session_state['publico'] = d.get('avatar', 'Emprendedores')
                    st.json(d)
                    st.success("¡Datos guardados en memoria!")
                except:
                    st.write(res)

    else:
        st.info("Ingresa los datos manualmente para empezar a fabricar.")
        col1, col2 = st.columns(2)
        with col1: t_man = st.text_input("Tu Tema:", value=st.session_state['tema'])
        with col2: p_man = st.text_input("Tu Público:", value=st.session_state['publico'])
        
        if st.button("💾 Guardar Datos Manuales"):
            st.session_state['tema'] = t_man
            st.session_state['publico'] = p_man
            st.success("¡Datos guardados! Ve a la siguiente pestaña.")

# ================= TAB 2: FÁBRICA (EBOOKS) =================
with tab2:
    st.markdown('<div class="header-style">🏭 Fábrica de Contenido</div>', unsafe_allow_html=True)
    
    st.write(f"**Trabajando sobre:** {st.session_state['tema']} | **Para:** {st.session_state['publico']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📑 1. Generar Índice del Ebook"):
            prompt = f"Crea un índice irresistible de 5 capítulos para un ebook sobre '{st.session_state['tema']}' para '{st.session_state['publico']}'. Solo titulos."
            res = consultar_gemini(prompt, api_key_google, modelo_actual)
            st.session_state['indice'] = res
            st.rerun()
            
    with col2:
        if st.button("✍️ 2. Escribir Contenido Completo"):
            if not st.session_state['indice']:
                st.error("Primero genera el índice.")
            else:
                prompt = f"Escribe el contenido COMPLETO del ebook basado en este índice:\n{st.session_state['indice']}\n\nTema: {st.session_state['tema']}. Tono: Persuasivo y práctico. Usa formato Markdown."
                with st.spinner("La IA está escribiendo tu libro..."):
                    res = consultar_gemini(prompt, api_key_google, modelo_actual)
                    st.markdown(res)

    if st.session_state['indice']:
        st.text_area("Índice Actual:", value=st.session_state['indice'], height=150)

# ================= TAB 3: PORTADA =================
with tab3:
    st.markdown('<div class="header-style">🎨 Generador de Arte</div>', unsafe_allow_html=True)
    estilo = st.selectbox("Estilo Visual:", ["Minimalista", "3D Pixar Style", "Fotorealista", "Cyberpunk", "Acuarela"])
    
    if st.button("✨ Generar Prompt para Imagen"):
        prompt = f"Describe un prompt DETALLADO en inglés para generar una portada de ebook sobre '{st.session_state['tema']}'. Estilo: {estilo}. High resolution, 8k."
        res = consultar_gemini(prompt, api_key_google, modelo_actual)
        st.code(res, language="text")
        st.info("Copia el texto de arriba y úsalo en Midjourney, Dall-E o Bing Image Creator.")

# ================= TAB 4: MARKETING =================
with tab4:
    st.markdown('<div class="header-style">📢 Kit de Marketing</div>', unsafe_allow_html=True)
    tipo_copy = st.selectbox("¿Qué necesitas redactar?", ["Email de Venta (Secuencia Soap Opera)", "Anuncio de Facebook Ads", "Post de Instagram (AIDA)", "Guion de Video (VSL)"])
    
    if st.button("📝 Redactar Copy"):
        prompt = f"Actúa como un copywriter experto (tipo Dan Kennedy). Escribe un '{tipo_copy}' para vender el ebook sobre '{st.session_state['tema']}' dirigido a '{st.session_state['publico']}'. Hazlo persuasivo."
        res = consultar_gemini(prompt, api_key_google, modelo_actual)
        st.markdown(res)

# ================= TAB 5: LANDING PAGE =================
with tab5:
    st.markdown('<div class="header-style">🌐 Constructor Web (Landing V2)</div>', unsafe_allow_html=True)
    st.info("Genera el código HTML listo para copiar y pegar.")
    
    if st.button("🔨 Construir Landing Page"):
        prompt = f"Escribe el código HTML5 completo (con CSS integrado en <style> muy moderno y bonito, colores oscuros y ne
