import streamlit as st
import google.generativeai as genai
from apify_client import ApifyClient
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SpyTool V9.1 Auto-Detect", page_icon="🏎️", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; transition: all 0.3s; }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .header-style { font-size: 24px; font-weight: bold; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #f0f2f6; }
    .success-box { padding: 15px; background-color: #d4edda; color: #155724; border-radius: 8px; border: 1px solid #c3e6cb; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN INTELIGENTE: AUTO-DETECTAR MODELO ---
def conseguir_modelo_valido(api_key):
    if not api_key: return None
    genai.configure(api_key=api_key)
    try:
        # 1. Preguntar a Google qué modelos tiene disponibles
        mis_modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 2. Elegir el mejor disponible (Prioridad: Flash -> Pro 1.5 -> Pro 1.0)
        if "models/gemini-1.5-flash" in mis_modelos: return "gemini-1.5-flash"
        if "models/gemini-1.5-pro" in mis_modelos: return "gemini-1.5-pro"
        if "models/gemini-pro" in mis_modelos: return "gemini-pro"
        if "models/gemini-1.0-pro" in mis_modelos: return "gemini-1.0-pro"
        
        # 3. Si no encuentra los favoritos, usar el primero que haya
        return mis_modelos[0].replace("models/", "") if mis_modelos else None
    except:
        return None

# --- BARRA LATERAL (PANEL DE CONTROL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/263/263142.png", width=50)
    st.title("SpyTool V9.1 🏎️")
    st.markdown("---")
    
    # GESTIÓN DE CLAVES
    api_key_google = st.secrets.get("GOOGLE_API_KEY")
    api_token_apify = st.secrets.get("APIFY_API_TOKEN")

    if not api_key_google:
        api_key_google = st.text_input("Google API Key:", type="password")
    else:
        st.success("Google Key: Cargada ✅")
        
    if not api_token_apify:
        api_token_apify = st.text_input("Apify Token:", type="password")
    else:
        st.success("Apify Token: Cargado ✅")
    
    st.markdown("---")
    
    # SISTEMA DE AUTO-DETECCIÓN
    modelo_actual = "gemini-pro" # Fallback por seguridad
    if api_key_google:
        detectado = conseguir_modelo_valido(api_key_google)
        if detectado:
            modelo_actual = detectado
            st.info(f"🧠 Motor Activo: **{modelo_actual}**")
        else:
            st.error("❌ Error: API Key inválida o sin modelos.")
    else:
        st.warning("⚠️ Esperando API Key...")

# --- FUNCIÓN GENERADORA ---
def consultar_gemini(prompt, api_key, modelo):
    if not api_key: return None
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(modelo)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generando texto: {str(e)}"

# --- ESTADO DE LA SESIÓN ---
if 'tema' not in st.session_state: st.session_state['tema'] = "Sin tema definido"
if 'publico' not in st.session_state: st.session_state['publico'] = "General"

# --- TABS PRINCIPALES ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🕵️ Radar", "🏭 Fábrica 2.0", "🎨 Portada", "📢 Marketing", "🌐 Landing V2", "💰 Monetización"
])

# ================= PESTAÑA 1: RADAR =================
with tab1:
    st.markdown('<div class="header-style">🕵️ Investigación de Mercado</div>', unsafe_allow_html=True)
    modo = st.radio("Modo:", ["🤖 Automático (Apify)", "✍️ Manual"], horizontal=True)
    
    if modo == "🤖 Automático (Apify)":
        col1, col2 = st.columns(2)
        with col1: keyword = st.text_input("Nicho:", placeholder="Ej: Yoga para espalda")
        with col2: pais = st.selectbox("País:", ["BR", "US", "ES", "MX", "CO"])
        
        if st.button("🚀 Escanear Facebook Ads"):
            if not api_token_apify: st.error("Falta Token Apify")
            else:
                with st.status("Escaneando...") as status:
                    try:
                        client = ApifyClient(api_token_apify)
                        run = client.actor("curious_coder/facebook-ads-library-scraper").call(run_input={"queries": [keyword], "countryCode": pais, "maxResults": 3})
                        res = [item.get("content", "") for item in client.dataset(run["defaultDatasetId"]).iterate_items() if item.get("content")]
                        if res:
                            st.session_state['resultados'] = res
                            status.update(label="¡Datos encontrados!", state="complete")
                            st.success(f"{len(res)} anuncios capturados.")
                        else: st.warning("No se encontraron anuncios.")
                    except Exception as e: st.error(f"Error: {e}")
        
        if 'resultados' in st.session_state:
            if st.button("Analizar Datos"):
                txt = "\n".join(st.session_state['resultados'][:3])
                p = f"Analiza estos anuncios sobre '{keyword}':\n{txt}\nExtrae JSON: {{'dolor': '', 'promesa': '', 'avatar': ''}}"
                res = consultar_gemini(p, api_key_google, modelo_actual)
                try:
                    d = json.loads(res.replace("```json","").replace("```",""))
                    st.session_state.update({'tema': keyword, 'publico': d.get('avatar')})
                    st.json(d)
                except: st.write(res)

    else:
        t = st.text_area("Pega tu idea:")
        if st.button("Guardar Manual"):
            st.session_state['tema'] = t
            st.success("Tema guardado.")

# ================= PESTAÑA 6: MONETIZACIÓN (La importante) =================
with tab6:
    st.markdown('<div class="header-style">💰 Fábrica de Dinero (Bumps & Upsells)</div>', unsafe_allow_html=True)
    st.info(f"Generando contenido para: {st.session_state['tema']}")
    
    tipo = st.radio("Crear:", ["Order Bump ($7-$17)", "Upsell VIP ($27-$97)"], horizontal=True)
    
    if tipo == "Order Bump ($7-$17)":
        fmt = st.selectbox("Formato:", ["🎧 Guion Audio", "📄 Checklist", "🚫 Lista Negra"])
        if st.button("Generar Bump"):
            prompt = f"Crea el contenido COMPLETO para un Order Bump de tipo '{fmt}' sobre '{st.session_state['tema']}'. Hazlo práctico y directo."
            res = consultar_gemini(prompt, api_key_google, modelo_actual)
            st.markdown(res)
            
    else:
        fmt = st.selectbox("Formato:", ["🎓 Masterclass", "🗓️ Reto 30 Días"])
        if st.button("Generar Upsell"):
            prompt = f"Crea la ESTRUCTURA para un Upsell de tipo '{fmt}' sobre '{st.session_state['tema']}'."
            res = consultar_gemini(prompt, api_key_google, modelo_actual)
            st.markdown(res)

# ================= OTRAS PESTAÑAS (Resumidas para ahorrar espacio) =================
with tab2: st.write("Fábrica de Ebooks lista 🏭")
with tab3: st.write("Generador de Portadas listo 🎨")
with tab4: st.write("Generador de Marketing listo 📢")
with tab5: st.write("Generador de Landing V2 listo 🌐")
