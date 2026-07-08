import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time
import io
import urllib.parse

# --- DICCIONARIOS INVERTIDOS ---
capacidades_base = {
    "15 cm": 6, "20 cm": 15, "25 cm": 25, "30 cm": 40,
    "35 cm": 60, "40 cm": 80, "45 cm": 100, "50 cm": 120
}

capacidades_plancha = {
    "31x21 cm": 40, "36x28 cm": 60, "41x30 cm": 80,
    "54x37 cm": 100, "63x37 cm": 120
}

# --- FUNCIONES DE LÓGICA Y DIBUJO ---
def extraer_ancho(medida_str):
    if "x" in medida_str:
        return int(medida_str.split("x")[0])
    return int(medida_str.split()[0])

def agrupar_pisos(dimensiones):
    dimensiones_ordenadas = sorted(dimensiones, key=extraer_ancho, reverse=True)
    pisos = []
    for dim in dimensiones_ordenadas:
        if pisos and pisos[-1]['medida'] == dim:
            pisos[-1]['altura_cm'] += 6
            pisos[-1]['cantidad_bases'] += 1
        else:
            pisos.append({'medida': dim, 'altura_cm': 6, 'cantidad_bases': 1})
    return pisos

def dibujar_esquema(pisos_agrupados, relleno, tipo):
    fig, ax = plt.subplots(figsize=(6, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 140) 
    ax.axis('off')
    
    # Plato
    plato = patches.Ellipse((50, 20), 80, 10, color='saddlebrown')
    ax.add_patch(plato)
    
    y_inicio = 20
    altura_total_dibujo = 0
    altura_total_cm = 0
    
    for i, piso in enumerate(pisos_agrupados):
        medida = piso['medida']
        altura_cm = piso['altura_cm']
        
        ancho_real = extraer_ancho(medida)
        ancho_dibujo = ancho_real * 1.5 
        altura_dibujo = altura_cm * 2.5 
        x_inicio = 50 - (ancho_dibujo / 2)
        
        pastel = patches.Rectangle((x_inicio, y_inicio), ancho_dibujo, altura_dibujo, 
                                   linewidth=2, edgecolor='black', facecolor='seashell')
        ax.add_patch(pastel)
        
        etiqueta_ancho = f"{medida} dia." if tipo == "Tipo Base (Redondo)" else medida
        ax.text(50, y_inicio + (altura_dibujo/2), etiqueta_ancho, 
                va='center', ha='center', fontsize=10, fontweight='bold', color='black')
        
        ax.text(x_inicio - 2, y_inicio + (altura_dibujo/2), f"{altura_cm} cm\n({piso['cantidad_bases']} bases)", 
                va='center', ha='right', fontsize=9, color='blue')
        
        y_inicio += altura_dibujo
        altura_total_dibujo += altura_dibujo
        altura_total_cm += altura_cm
        
    ax.annotate('', xy=(88, 20), xytext=(88, 20 + altura_total_dibujo),
                arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5))
    ax.text(91, 20 + altura_total_dibujo/2, f'Total:\n{altura_total_cm} cm', 
            va='center', ha='left', fontsize=12, fontweight='bold')
    
    ax.text(50, y_inicio + 8, f'Relleno: {relleno}', va='center', ha='center', 
            fontsize=11, fontstyle='italic', color='dimgray')
    
    return fig

# --- FUNCIÓN REINICIAR ---
def reiniciar_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Creador de Pasteles", layout="centered")
st.title("🎂 Creador de Pasteles")
st.write("Selecciona los diámetros y el sistema calculará las porciones y armará el diseño.")
st.divider()

# --- 1. DATOS PRINCIPALES ---
tipo = st.selectbox("1. Tipo de Pastel:", ["Tipo Base (Redondo)", "Tipo Plancha (Rectangular)"], index=None, placeholder="Selecciona el tipo...", key="in_tipo")
relleno = st.text_input("2. Relleno:", value="", placeholder="Ej. Fresa con Crema", key="in_relleno")

opciones_medidas = []
diccionario_actual = {}
if tipo == "Tipo Base (Redondo)":
    opciones_medidas = list(capacidades_base.keys())
    diccionario_actual = capacidades_base
elif tipo == "Tipo Plancha (Rectangular)":
    opciones_medidas = list(capacidades_plancha.keys())
    diccionario_actual = capacidades_plancha

# --- 2. CONFIGURACIÓN DE MEDIDAS (BASES) ---
st.divider()
num_bases = st.number_input("3. ¿Cuántos pasteles (bases de 6 cm) vas a apilar?", min_value=1, max_value=6, value=None, placeholder="Ej. 2", key="in_bases")

dimensiones_ingresadas = []

if num_bases is not None and tipo is not None:
    st.write("**Selecciona la medida de cada base agregada:**")
    st.info("💡 Tip: Si seleccionas dos bases de la misma medida, se fusionarán en un piso de doble altura (12 cm).")
    
    for i in range(num_bases):
        dim = st.selectbox(f"Medida de la base {i+1}", opciones_medidas, index=None, placeholder="Selecciona medida...", key=f"in_dim_{i}")
        dimensiones_ingresadas.append(dim)

st.divider()

# Usamos variables persistidas en session_state para mantener el resultado visible
if "calculado" not in st.session_state:
    st.session_state.calculado = False

# --- 3. BOTÓN DE CALCULAR ---
if st.button("🚀 Calcular y Generar Esquema", type="primary"):
    if tipo is None or not relleno or num_bases is None or None in dimensiones_ingresadas:
        st.error("⚠️ Por favor, llena todos los campos y selecciona la medida de todas las bases antes de calcular.")
    else:
        with st.spinner('Ensamblando el pastel y calculando porciones...'):
            time.sleep(1.5) 
        
        # Guardar resultados en el estado de la sesión
        st.session_state.total_personas = sum([diccionario_actual[dim] for dim in dimensiones_ingresadas])
        st.session_state.pisos_agrupados = agrupar_pisos(dimensiones_ingresadas)
        st.session_state.altura_total = sum([piso['altura_cm'] for piso in st.session_state.pisos_agrupados])
        st.session_state.tipo_guardado = tipo
        st.session_state.relleno_guardado = relleno
        st.session_state.num_bases_guardado = num_bases
        st.session_state.calculado = True

# --- MOSTRAR RESULTADOS SI YA SE CALCULÓ ---
if st.session_state.calculado:
    st.success("¡Esquema generado con éxito!")
    
    # Resumen
    st.subheader("📊 Resumen del Pedido")
    st.write(f"👥 **Capacidad total:** Alcanza para **{st.session_state.total_personas} personas**.")
    st.write(f"🥞 **Total de bases (6cm c/u):** {st.session_state.num_bases_guardado}")
    st.write(f"🍰 **Pisos resultantes (visibles):** {len(st.session_state.pisos_agrupados)}")
    st.write(f"📏 **Altura total:** {st.session_state.altura_total} cm")

    # Visual
    st.subheader("📐 Esquema Visual")
    fig = dibujar_esquema(st.session_state.pisos_agrupados, st.session_state.relleno_guardado, st.session_state.tipo_guardado)
    st.pyplot(fig)
    
    # --- PROCESAMIENTO DE IMAGEN PARA DESCARGA ---
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    
    # --- CONSTRUCCIÓN DEL MENSAJE DE WHATSAPP ---
    texto_wa = f"*Resumen de Pedido de Pastel*\n\n"
    texto_wa += f"• *Tipo:* {st.session_state.tipo_guardado}\n"
    texto_wa += f"• *Relleno:* {st.session_state.relleno_guardado}\n"
    texto_wa += f"• *Bases totales:* {st.session_state.num_bases_guardado} de 6cm c/u\n"
    texto_wa += f"• *Altura Total:* {st.session_state.altura_total} cm\n\n"
    texto_wa += f"📊 *Distribución de pisos:*\n"
    for p in st.session_state.pisos_agrupados:
        texto_wa += f"  - Medida: {p['medida']} | Altura: {p['altura_cm']} cm ({p['cantidad_bases']} bases)\n"
    texto_wa += f"\n👥 *Capacidad Calculada:* ¡Para {st.session_state.total_personas} personas!"
    
    texto_wa_encoded = urllib.parse.quote(texto_wa)
    whatsapp_url = f"https://wa.me/?text={texto_wa_encoded}"
    
    # --- BOTONES DE ACCIÓN ADICIONALES ---
    col_down, col_wa = st.columns(2)
    with col_down:
        st.download_button(
            label="💾 Descargar Diagrama (PNG)",
            data=buf,
            file_name="esquema_pastel.png",
            mime="image/png",
            use_container_width=True
        )
    with col_wa:
        st.link_button("💬 Enviar por WhatsApp", whatsapp_url, use_container_width=True)

# --- BOTÓN BORRAR TODO (HASTA ABAJO) ---
st.write("")
st.write("")
st.divider()
st.button("🗑️ Borrar Todo y Limpiar Campos", on_click=reiniciar_app, type="secondary", use_container_width=True)
