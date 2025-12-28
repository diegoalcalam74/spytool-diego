import streamlit as st
import google.generativeai as genai
from apify_client import ApifyClient
import json
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SpyTool V9.3 Final", page_icon="🏎️", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; transition: all 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .header-style { font-size: 24px; font-weight: bold; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #f0f2f6; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN AUTO-DETECTAR MODELO ---
def conseguir_modelo_valido(api_key):
    if not api_key: return None
    genai.configure(api_key=api_key)
    try:
        mis_modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if "models/gemini-1.5-flash" in mis_modelos: return "gemini-1.5-flash"
        if "models/gemini-1.5-pro" in mis_modelos: return "gemini-1.5-pro"
        if "models/gemini-pro" in mis_modelos: return "gemini-pro"
        return mis_modelos[0].replace("models/", "") if mis_modelos else None
    except:
        return None

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("SpyTool V9.3 🏎️")
    st.markdown("---")
    
    api_key_google = st.secrets.get("GOOGLE_API_KEY")
    api_token_apify = st.secrets.get("APIFY_API_TOKEN")

    if not api_key_google:
        api_key_google = st.text_input("Google API Key:", type="password")
    
    if not api_token_apify:
        api_token_apify = st.text_input("Apify Token:", type="password")
    
    modelo_actual = "gemini-pro"
    if api_key_google:
        detectado = conseguir_modelo_valido(api_key_google)
        if detectado:
            modelo_actual = detectado
            st.success(f"✅ Motor: {modelo_actual}")
        else:
            st.error("❌ Revisa tu API Key")

# --- FUNCIÓN GENERADORA ---
def consultar_gemini(prompt, api_key, modelo):
    if not api_key: return "⚠️ Falta API Key"
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(modelo)
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Error: {str(e)}"

# --- MEMORIA ---
if 'tema' not in st.session_state: st.session_state['tema'] = ""
if 'publico' not in st.session_state: st.session_state['publico'] = ""
if 'indice' not in st.session_state: st.session_state['indice'] = ""
if 'resultados_radar' not in st.session_state: st.session_state['resultados_radar'] = []

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🕵️ Radar", "🏭 Fábrica", "🎨 Portada", "📢 Marketing", "🌐 Landing", "💰 Monetización"
])

# 1. RADAR
with tab1:
    st.markdown('<div class="header-style">🕵️ Radar de Mercado</div>', unsafe_allow_html=True)
    modo = st.radio("Modo:", ["🤖 Automático (Apify)", "✍️ Manual"], horizontal=True)
    
    if modo == "🤖 Automático (Apify)":
        col1, col2 = st.columns(2)
        with col1: keyword = st.text_input("Nicho:", placeholder="Ej: Yoga")
        with col2: pais = st.selectbox("País:", ["BR", "US", "ES", "MX"])
        
        if st.button("🚀 Escanear"):
            if not api_token_apify: st.error("Falta Token Apify")
            else:
                try:
                    client = ApifyClient(api_token_apify)
                    run = client.actor("curious_coder/facebook-ads-library-scraper").call(run_input={"queries": [keyword], "countryCode": pais, "maxResults": 3})
                    res = [item.get("content", "") for item in client.dataset(run["defaultDatasetId"]).iterate_items() if item.get("content")]
                    if res:
                        st.session_state['resultados_radar'] = res
                        st.success(f"{len(res)} anuncios encontrados.")
                        
                        # Analizar automáticamente con comillas triples seguras
                        txt = "\n".join(res[:3])
                        p = f"""Analiza estos anuncios de '{keyword}':
                        {txt}
                        Extrae JSON: {{'dolor': '', 'promesa': '', 'avatar': ''}}"""
                        analisis = consultar_gemini(p, api_key_google, modelo_actual)
                        try:
                            d = json.loads(analisis.replace("```json","").replace("```",""))
                            st.session_state['tema'] = keyword
                            st.session_state['publico'] = d.get('avatar')
                            st.json(d)
                        except: st.write(analisis)
                    else: st.warning("Nada encontrado.")
                except Exception as e: st.error(f"Error: {e}")

    else:
        c1, c2 = st.columns(2)
        with c1: t = st.text_input("Tema:", value=st.session_state['tema'])
        with c2: p = st.text_input("Público:", value=st.session_state['publico'])
        if st.button("Guardar"):
            st.session_state['tema'] = t
            st.session_state['publico'] = p
            st.success("Guardado")

# 2. FÁBRICA
with tab2:
    st.markdown('<div class="header-style">🏭 Fábrica Ebooks</div>', unsafe_allow_html=True)
    st.write(f"Tema: **{st.session_state['tema']}**")
    
    if st.button("1. Generar Índice"):
        # USAMOS COMILLAS TRIPLES PARA EVITAR ERRORES
        p = f"""Crea un índice de 5 capítulos para un ebook sobre '{st.session_state['tema']}' 
        dirigido a '{st.session_state['publico']}'. Solo titulos."""
        st.session_state['indice'] = consultar_gemini(p, api_key_google, modelo_actual)
        st.rerun()
        
    if st.session_state['indice']:
        st.text_area("Índice:", value=st.session_state['indice'])
        if st.button("2. Escribir Libro"):
            p = f"""Escribe el contenido completo del ebook basado en:
            {st.session_state['indice']}
            Tema: {st.session_state['tema']}."""
            with st.spinner("Escribiendo..."):
                st.markdown(consultar_gemini(p, api_key_google, modelo_actual))

# 3. PORTADA
with tab3:
    st.markdown('<div class="header-style">🎨 Portada</div>', unsafe_allow_html=True)
    estilo = st.selectbox("Estilo:", ["Minimalista", "3D", "Fotorealista"])
    if st.button("Generar Prompt Imagen"):
        p = f"""Describe un prompt en inglés para generar una portada de ebook 
        sobre '{st.session_state['tema']}' estilo {estilo}."""
        st.code(consultar_gemini(p, api_key_google, modelo_actual))

# 4. MARKETING
with tab4:
    st.markdown('<div class="header-style">📢 Marketing</div>', unsafe_allow_html=True)
    tipo = st.selectbox("Tipo:", ["Email Venta", "Anuncio FB", "Post IG"])
    if st.button("Generar Copy"):
        p = f"""Escribe un {tipo} persuasivo para vender el ebook '{st.session_state['tema']}'."""
        st.markdown(consultar_gemini(p, api_key_google, modelo_actual))

# 5. LANDING (EL ERROR ESTABA AQUÍ, YA CORREGIDO CON TRIPLES COMILLAS)
with tab5:
    st.markdown('<div class="header-style">🌐 Landing Page</div>', unsafe_allow_html=True)
    if st.button("Crear Web"):
        prompt = f"""Escribe el código HTML5 completo con CSS integrado moderno 
        para una Landing Page que venda un producto sobre '{st.session_state['tema']}'. 
        Incluye Hero, Beneficios y CTA."""
        st.code(consultar_gemini(prompt, api_key_google, modelo_actual), language="html")

# 6. MONETIZACIÓN
with tab6:
    st.markdown('<div class="header-style">💰 Monetización</div>', unsafe_allow_html=True)
    tipo = st.radio("Crear:", ["Order Bump", "Upsell"])
    if st.button("Generar Producto Extra"):
        p = f"""Crea el contenido para un {tipo} sobre '{st.session_state['tema']}'. 
        Hazlo práctico y directo."""
        st.markdown(consultar_gemini(p, api_key_google, modelo_actual))
