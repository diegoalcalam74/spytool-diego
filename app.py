import streamlit as st
import google.generativeai as genai
from apify_client import ApifyClient
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SpyTool Pro: V9.0 Monetización", page_icon="🏎️", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS (PARA QUE SE VEA COMO FERRARI) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .header-style {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #f0f2f6;
    }
    .success-box {
        padding: 15px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin-bottom: 15px;
    }
    .warning-box {
        padding: 15px;
        background-color: #fff3cd;
        color: #856404;
        border-radius: 8px;
        border: 1px solid #ffeeba;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE SECRETOS ---
api_key_google = st.secrets.get("GOOGLE_API_KEY")
api_token_apify = st.secrets.get("APIFY_API_TOKEN")

# --- BARRA LATERAL (PANEL DE CONTROL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/263/263142.png", width=50)
    st.title("SpyTool Pro V9.0")
    st.markdown("---")
    
    st.subheader("🔑 Llaves de Acceso")
    if not api_key_google:
        api_key_google = st.text_input("Tu Google API Key:", type="password")
    else:
        st.success("Google Key: Cargada ✅")
        
    if not api_token_apify:
        api_token_apify = st.text_input("Tu Apify Token:", type="password")
    else:
        st.success("Apify Token: Cargado ✅")
    
    st.markdown("---")
    
    # Modelos Gemini disponibles
   # Usamos "gemini-pro" al principio porque NUNCA falla
   # Ahora que tenemos librería 0.8.3, Flash funcionará perfecto
    mis_modelos = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"]
    modelo_seleccionado = st.selectbox("🧠 Modelo Cerebral:", mis_modelos, index=0)
    
    st.info(f"Modo actual: {modelo_seleccionado}")

# --- FUNCIÓN MAESTRA DE CONSULTA A GEMINI ---
def consultar_gemini_robusto(prompt, api_key, modelo, lista_modelos):
    if not api_key:
        st.error("⚠️ Falta la Google API Key en la barra lateral.")
        return None
        
    genai.configure(api_key=api_key)
    
    # Intentar primero con el modelo seleccionado
    try:
        model = genai.GenerativeModel(modelo)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Si falla, intentar con otros modelos (fallback)
        st.warning(f"El modelo {modelo} falló, intentando con respaldo...")
        for m in lista_modelos:
            if m != modelo:
                try:
                    model = genai.GenerativeModel(m)
                    response = model.generate_content(prompt)
                    return response.text
                except:
                    continue
        st.error(f"Error total: {e}")
        return None

# --- ESTADO DE LA SESIÓN (MEMORIA TEMPORAL) ---
if 'tema' not in st.session_state:
    st.session_state['tema'] = "Sin tema definido aún"
if 'publico' not in st.session_state:
    st.session_state['publico'] = "General"

# --- TABS PRINCIPALES ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🕵️ Radar", 
    "🏭 Fábrica 2.0", 
    "🎨 Portada Pro", 
    "📢 Marketing", 
    "🌐 Landing V2",
    "💰 Monetización"
])

# ==============================================================================
# PESTAÑA 1: RADAR (INVESTIGACIÓN)
# ==============================================================================
with tab1:
    st.markdown('<div class="header-style">🕵️ Investigación de Mercado</div>', unsafe_allow_html=True)
    
    modo_busqueda = st.radio("Modo:", ["🤖 Automático (Apify)", "✍️ Manual (Pegar Texto)"], horizontal=True)
    
    if modo_busqueda == "🤖 Automático (Apify)":
        col1, col2 = st.columns(2)
        with col1:
            keyword = st.text_input("Nicho / Palabra Clave:", placeholder="Ej: Yoga para espalda")
        with col2:
            pais = st.selectbox("País Objetivo:", ["BR", "US", "ES", "MX", "CO"], index=0)
            
        if st.button("🚀 Escanear Facebook Ads"):
            if not api_token_apify:
                st.error("Necesitas el Token de Apify en la barra lateral.")
            else:
                with st.status("Iniciando escaneo satelital...", expanded=True) as status:
                    try:
                        client = ApifyClient(api_token_apify)
                        run_input = {
                            "queries": [keyword],
                            "countryCode": pais,
                            "maxResults": 3
                        }
                        status.write("🛰️ Contactando satélite de anuncios...")
                        run = client.actor("curious_coder/facebook-ads-library-scraper").call(run_input=run_input)
                        
                        resultados = []
                        status.write("📥 Descargando datos...")
                        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                            content = item.get("content", "")
                            if content:
                                resultados.append(content)
                        
                        if resultados:
                            st.session_state['resultados_raw'] = resultados
                            status.update(label="¡Datos recibidos!", state="complete", expanded=False)
                            st.success(f"Se capturaron {len(resultados)} anuncios ganadores.")
                        else:
                            status.update(label="Sin resultados", state="error")
                            st.warning("No se encontraron anuncios. Intenta una palabra más general.")
                            
                    except Exception as e:
                        st.error(f"Error en el radar: {str(e)}")

        if 'resultados_raw' in st.session_state and st.session_state['resultados_raw']:
            st.write("---")
            st.subheader("🧠 Análisis de Inteligencia")
            if st.button("Analizar Patrones Ganadores"):
                texto_anuncios = "\n\n".join(st.session_state['resultados_raw'][:3])
                prompt_analisis = f"""
                Analiza estos textos de anuncios reales sobre '{keyword}':
                {texto_anuncios}
                
                Dime:
                1. Cuál es el DOLOR principal que atacan.
                2. Qué PROMESA están haciendo.
                3. Define el perfil exacto del cliente (Avatar).
                
                Responde en formato JSON simple: {{ "dolor": "...", "promesa": "...", "avatar": "..." }}
                """
                res = consultar_gemini_robusto(prompt_analisis, api_key_google, modelo_seleccionado, mis_modelos)
                if res:
                    try:
                        datos = json.loads(res.replace("```json", "").replace("```", ""))
                        st.session_state['tema'] = keyword
                        st.session_state['publico'] = datos.get("avatar", "General")
                        
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>🎯 Objetivo Identificado</h4>
                            <p><b>Dolor Detectado:</b> {datos.get('dolor')}</p>
                            <p><b>Promesa Ganadora:</b> {datos.get('promesa')}</p>
                            <p><b>Público:</b> {datos.get('avatar')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except:
                        st.write(res)

    else: # MODO MANUAL
        texto_manual = st.text_area("Pega tu idea o anuncio ganador:", height=150)
        if st.button("Analizar Texto Manual"):
            st.session_state['tema'] = texto_manual[:50] + "..."
            st.session_state['publico'] = "Definido manualmente"
            st.success("Concepto cargado manualmente. Ve a la Fábrica.")

# ==============================================================================
# PESTAÑA 2: FÁBRICA 2.0 (BOOK CREATOR)
# ==============================================================================
with tab2:
    st.markdown('<div class="header-style">🏭 Fábrica de Ebooks 2.0</div>', unsafe_allow_html=True)
    
    if st.session_state['tema'] == "Sin tema definido aún":
        st.warning("⚠️ Primero define un tema en la pestaña 'Radar'.")
    else:
        st.info(f"📌 Concepto Base: {st.session_state['tema']}")
    
    col_ind, col_write = st.columns([1, 2])
    
    with col_ind:
        st.subheader("1. Estructura")
        if st.button("Generar Índice 'Tool-kit'"):
            prompt_indice = f"""
            Crea un índice para un Ebook corto y accionable (Ebook 2.0) sobre: {st.session_state['tema']}.
            NO quiero teoría aburrida. Quiero:
            - 5 Capítulos máximo.
            - Títulos gancheros (Ej: "La técnica de 5 minutos", "Tu plan de emergencia").
            - Enfocado en resultados rápidos.
            """
            res = consultar_gemini_robusto(prompt_indice, api_key_google, modelo_seleccionado, mis_modelos)
            if res:
                st.session_state['indice_generado'] = res
        
        if 'indice_generado' in st.session_state:
            st.text_area("Índice Sugerido:", value=st.session_state['indice_generado'], height=300)

    with col_write:
        st.subheader("2. Escritura Inteligente")
        titulo_cap = st.text_input("Título del Capítulo a escribir:")
        
        tipo_contenido = st.selectbox("Tipo de Contenido:", [
            "📖 Lección + Ejercicio (Workbook)",
            "✅ Checklist de Acción",
            "⚡ Reto de 24 Horas",
            "📱 Híbrido (Texto + Video QR)"
        ])
        
        detalles_extra = st.text_area("Instrucciones extra para la IA:", placeholder="Ej: Usa un tono motivador, incluye una anécdota...")
        
        if st.button("✍️ Escribir Capítulo Pro"):
            prompt_cap = f"""
            Escribe el capítulo '{titulo_cap}' para un libro sobre {st.session_state['tema']}.
            ESTILO: {tipo_contenido}.
            PÚBLICO: {st.session_state['publico']}.
            INSTRUCCIONES: {detalles_extra}.
            
            REGLAS DE FORMATO OBLIGATORIAS:
            1. Usa Markdown (negritas, títulos).
            2. Si es 'Workbook', incluye líneas para escribir así: __________
            3. Si es 'Checklist', usa casillas así: [ ] Tarea 1.
            4. Si es 'Híbrido', incluye un recuadro grande que diga EXACTAMENTE:
               ***
               📱 [ESPACIO PARA CÓDIGO QR]
               (Escanea para ver el video explicativo)
               ***
            5. AL FINAL, agrega un recuadro con un "Prompt de IA" para que el usuario lo copie y pegue en ChatGPT.
            """
            res = consultar_gemini_robusto(prompt_cap, api_key_google, modelo_seleccionado, mis_modelos)
            if res:
                st.markdown("### Vista Previa:")
                st.markdown(res)
                
                # Guardar en acumulado
                if 'ebook_completo' not in st.session_state:
                    st.session_state['ebook_completo'] = ""
                st.session_state['ebook_completo'] += f"\n\n# {titulo_cap}\n\n{res}"
                st.success("Capítulo añadido al borrador.")

    st.markdown("---")
    st.subheader("📦 Exportación")
    if 'ebook_completo' in st.session_state and st.session_state['ebook_completo']:
        st.download_button("📥 Descargar Ebook Completo (.txt / Markdown)", st.session_state['ebook_completo'], "ebook_2_0.md")
        st.caption("Copia el contenido descargado y pégalo en Word o Canva.")

# ==============================================================================
# PESTAÑA 3: PORTADA PRO
# ==============================================================================
with tab3:
    st.markdown('<div class="header-style">🎨 Estudio de Diseño</div>', unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        titulo_libro = st.text_input("Título del Libro:", value="Guía Definitiva")
        estilo_visual = st.selectbox("Estilo Visual:", ["Fotorealista", "Minimalista Vectorial", "3D Render", "Estilo Revista Moderna"])
    
    with col_p2:
        st.info("Esta herramienta genera el 'Prompt' (Instrucción) para crear la imagen en Ideogram.ai")
    
    if st.button("🧠 Crear Prompt Ideogram"):
        prompt_imagen = f"""
        Actúa como experto en Midjourney e Ideogram.
        Escribe un PROMPT detallado en INGLÉS para generar una portada de Ebook profesional.
        
        TÍTULO DEL LIBRO: "{titulo_libro}" (Debe aparecer escrito en la imagen).
        TEMA: {st.session_state['tema']}.
        ESTILO: {estilo_visual}.
        
        El prompt debe describir: iluminación, tipografía, colores (psicología del color para este nicho) y composición.
        """
        res = consultar_gemini_robusto(prompt_imagen, api_key_google, modelo_seleccionado, mis_modelos)
        if res:
            st.code(res, language="text")
            st.success("Copia el texto de arriba y pégalo en Ideogram.ai")

# ==============================================================================
# PESTAÑA 4: MARKETING (ADS)
# ==============================================================================
with tab4:
    st.markdown('<div class="header-style">📢 Sala de Marketing</div>', unsafe_allow_html=True)
    
    tipo_copy = st.selectbox("¿Qué necesitas hoy?", ["Anuncio Facebook (Corto)", "Anuncio Facebook (Storytelling)", "Guion de Reel/TikTok (30 seg)", "Email de Venta"])
    
    if st.button("Generar Copy"):
        prompt_mkt = f"""
        Escribe un {tipo_copy} para vender el ebook sobre {st.session_state['tema']}.
        Público: {st.session_state['publico']}.
        
        Usa la fórmula AIDA (Atención, Interés, Deseo, Acción).
        Usa emojis.
        Si es Video, incluye indicaciones visuales [Corte a...].
        """
        res = consultar_gemini_robusto(prompt_mkt, api_key_google, modelo_seleccionado, mis_modelos)
        if res:
            st.markdown(res)

# ==============================================================================
# PESTAÑA 5: LANDING PAGE V2 (CON BUMP Y ESTILO)
# ==============================================================================
with tab5:
    st.markdown('<div class="header-style">🌐 Landing Page de Alta Conversión (V2)</div>', unsafe_allow_html=True)
    
    col_main, col_bump = st.columns(2)
    
    with col_main:
        st.subheader("Producto Principal")
        prod = st.text_input("Nombre Producto:", value=f"Ebook: {st.session_state['tema']}")
        prec = st.text_input("Precio Oferta:", value="$17 USD")
        beneficios = st.text_area("3 Beneficios Clave:", value="Rápido, Fácil, Sin estrés")
    
    with col_bump:
        st.subheader("Oferta Bump (Cajita Amarilla)")
        incluir_bump = st.checkbox("¿Incluir Order Bump?", value=True)
        bump_title = st.text_input("Título del Bump:", value="Audio-Hinojis para Dormir")
        bump_price = st.text_input("Precio Bump:", value="$7 USD")
        bump_desc = st.text_input("Promesa Corta del Bump:", value="Duerme en 5 minutos o menos.")
    
    if st.button("🏗️ Generar Web Moderna"):
        texto_bump = ""
        if incluir_bump:
            texto_bump = f"""
            INCLUYE CÓDIGO HTML PARA UN 'ORDER BUMP' justo encima del botón de compra final.
            Estilo del Bump: Fondo amarillo pálido (#fff3cd), borde punteado rojo (#dc3545), padding 15px.
            Debe tener un Checkbox visible. Texto: "SÍ, agregar {bump_title} por solo {bump_price}".
            Debajo del checkbox: "{bump_desc}".
            """
        
        prompt_web = f"""
        Actúa como Desarrollador Frontend Senior.
        Crea una Landing Page completa en un solo archivo HTML (con CSS incrustado en <style>).
        
        PRODUCTO: {prod}.
        PRECIO: {prec}.
        BENEFICIOS: {beneficios}.
        
        DISEÑO (CSS MODERN):
        - Fuente: 'Inter', sans-serif (impórtala de Google Fonts).
        - Fondo: Gris muy claro (#f8f9fa).
        - Contenedor principal: Blanco, centrado, ancho máx 700px, con sombra suave (box-shadow: 0 10px 30px rgba(0,0,0,0.1)).
        - Botón de Compra: Grande, ancho completo, color verde esmeralda o naranja brillante, con efecto hover.
        - Bordes redondeados en todo (border-radius: 12px).
        
        SECCIONES:
        1. Titular H1 centrado y poderoso.
        2. Subtítulo problema/agitación.
        3. Bullets points con iconos ✅.
        4. {texto_bump}
        5. Botón CTA: "DESCARGAR AHORA - {prec}".
        6. Footer con Copyright y Links (Privacidad | Términos).
        
        Solo entrega el código HTML. Nada más.
        """
        res = consultar_gemini_robusto(prompt_web, api_key_google, modelo_seleccionado, mis_modelos)
        if res:
            clean = res.replace("```html","").replace("```","")
            st.download_button("📥 Descargar HTML Listo", clean, "landing_pro.html")
            st.components.v1.html(clean, height=600, scrolling=True)

# ==============================================================================
# PESTAÑA 6: MONETIZACIÓN (BUMPS & UPSELLS) - NUEVA!
# ==============================================================================
with tab6:
    st.markdown('<div class="header-style">💰 Fábrica de Productos Extra (Monetización)</div>', unsafe_allow_html=True)
    st.info("Aquí crearás el CONTENIDO REAL para entregar cuando te compren el Bump o el Upsell.")
    
    tipo_extra = st.radio("¿Qué vas a fabricar?", ["Order Bump ($7-$17)", "Upsell VIP ($27-$97)"], horizontal=True)
    
    if tipo_extra == "Order Bump ($7-$17)":
        formato = st.selectbox("Formato del Bump:", [
            "🎧 Guion de Audio/Meditación (5 min)",
            "📄 Checklist Imprimible (1 Hoja)",
            "🚫 Lista Negra (Alimentos/Errores)",
            "📅 Menú/Plan Express de 3 Días"
        ])
        
        if st.button("Generar Contenido del Bump"):
            prompt_bump = f"""
            Actúa como experto en creación de infoproductos rápidos.
            El tema base es: {st.session_state['tema']}.
            
            Crea el CONTENIDO COMPLETO para un Order Bump tipo: {formato}.
            Objetivo: Debe ser algo que se consuma en menos de 10 minutos y dé una victoria rápida.
            
            Si es Audio: Escribe el guion palabra por palabra (incluye tono de voz).
            Si es Lista/Menú: Escribe la lista completa y organizada.
            
            Ponle un Título Irresistible al principio.
            """
            res = consultar_gemini_robusto(prompt_bump, api_key_google, modelo_seleccionado, mis_modelos)
            if res:
                st.markdown(res)
                st.download_button("📥 Descargar Contenido Bump", res, "contenido_bump.txt")
                
    else: # UPSELL
        formato_up = st.selectbox("Formato del Upsell:", [
            "🎓 Temario para Masterclass (Video)",
            "🗓️ Calendario de Reto 30 Días",
            "🤝 Script de Bienvenida Comunidad VIP",
            "📚 Pack de 10 Plantillas/Recetas"
        ])
        
        if st.button("Generar Estructura del Upsell"):
            prompt_upsell = f"""
            Actúa como creador de cursos online.
            El tema base es: {st.session_state['tema']}.
            
            Crea el CONTENIDO/ESTRUCTURA para un Upsell de alto valor tipo: {formato_up}.
            
            Si es Masterclass: Dame el esquema de los 3 módulos y los puntos clave de cada uno.
            Si es Reto 30 días: Dame la lista de tareas día por día (resumida).
            
            El objetivo es justificar un precio de $27 a $47 USD.
            """
            res = consultar_gemini_robusto(prompt_upsell, api_key_google, modelo_seleccionado, mis_modelos)
            if res:
                st.markdown(res)
                st.download_button("📥 Descargar Contenido Upsell", res, "contenido_upsell.txt")



