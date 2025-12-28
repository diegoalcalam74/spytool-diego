import streamlit as st
import google.generativeai as genai
from apify_client import ApifyClient
import json

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="SpyTool Pro: V9.1 Auto-Detect", page_icon="🏎️", layout="wide")

# --- ESTILOS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .header-style { font-size: 24px; font-weight: bold; border-bottom: 2px solid #f0f2f6; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN INTELIGENTE: AUTO-DETECTAR MODELO ---
def conseguir_modelo_valido(api_key):
    if not api_key: return None
    genai.configure(api_key=api_key)
    try:
        # Preguntamos a Google qué modelos tiene activos para esta cuenta
        lista_modelos = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                lista_modelos.append(m.name)
        
        # Prioridad: Flash -> Pro 1.5 -> Pro 1.0 -> El que haya
        if "models/gemini-1.5-flash" in lista_modelos: return "gemini-1.5-flash"
        if "models/gemini-1.5-pro" in lista_modelos: return "gemini-1.5-pro"
        if "models/gemini-pro" in lista_modelos: return "gemini-pro"
        
        # Si no encuentra favoritos, devuelve el primero de la lista
        if lista_modelos: return lista_modelos[0].replace("models/", "")
        return None
    except Exception as e:
        st.sidebar.error(f"Error conectando con Google: {str(e)}")
        return None

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("SpyTool V9.1 🏎️")
    
    # GESTIÓN DE CLAVES
    api_key_google = st.secrets.get("GOOGLE_API_KEY")
    api_token_apify = st.secrets.get("APIFY_API_TOKEN")

    if not api_key_google:
        api_key_google = st.text_input("Google API Key:", type="password")
    
    # AUTO-DETECCIÓN
    if api_key_google:
        modelo_detectado = conseguir_modelo_valido(api_key_google)
        if modelo_detectado:
            st.success(f"✅ Conectado a: {modelo_detectado}")
            modelo_actual = modelo_detectado
        else:
            st.error("❌ Tu API Key no encuentra modelos.")
            modelo_actual = "gemini-pro" # Fallback
    else:
        st.warning("⚠️ Falta API Key")
        modelo_actual = "gemini-pro"

# --- FUNCIÓN GENERADORA ---
def consultar_gemini(prompt, api_key, modelo):
    if not api_key: return None
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(modelo)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- TABS (Solo dejamos el de Monetización para probar rápido) ---
st.info("💡 Modo Diagnóstico activado. Si esto funciona, agregamos el resto.")
tab_moneda = st.tabs(["💰 Monetización"])

with tab_moneda[0]:
    st.header("Prueba de Fuego 🔥")
    if st.button("Generar Prueba Rápida"):
        res = consultar_gemini("Escribe una frase motivadora corta.", api_key_google, modelo_actual)
        st.success(res)
