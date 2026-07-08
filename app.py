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

def agrupar_pisos(bases_ingresadas):
    bases_ordenadas = sorted(bases_ingresadas, key=lambda x: extraer_ancho(x['medida']), reverse=True)
    pisos = []
    
    for base in bases_ordenadas:
        if pisos and pisos[-1]['medida'] == base['medida']:
            pisos[-1]['altura_cm'] += 6
            pisos[-1]['cantidad_bases'] += 1
            if base['relleno'] not in pisos[-1]['relleno']:
                pisos[-1]['relleno'] += " + " + base['relleno'] 
        else:
            pisos.append({
                'medida': base['medida'], 
                'altura_cm': 6, 
                'cantidad_bases': 1,
                'relleno': base['relleno']
            })
    return pisos

def dibujar_esquema(pisos_agrupados, tipo, tipo_relleno, relleno_global):
    fig, ax = plt.subplots(figsize=(6, 7))
    ax.axis('off')
    
    if tipo == "Tipo Base (Redondo)":
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 140) 
        
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
            
            etiqueta_centro = f"{medida} dia."
            if tipo_relleno == "Rellenos diferentes por base":
                etiqueta_centro += f"\n({piso['relleno']})"
                
            ax.text(50, y_inicio + (altura_dibujo/2), etiqueta_centro, 
                    va='center', ha='center', fontsize=9, fontweight='bold', color='black')
            
            ax.text(x_inicio - 2, y_inicio + (altura_dibujo/2), f"{altura_cm} cm\n({piso['cantidad_bases']} bases)", 
                    va='center', ha='right', fontsize=9, color='blue')
            
            y_inicio += altura_dibujo
            altura_total_dibujo += altura_dibujo
            altura_total_cm += altura_cm
            
        ax.annotate('', xy=(88, 20), xytext=(88, 20 + altura_total_dibujo),
                    arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5))
        ax.text(91, 20 + altura_total_dibujo/2, f'Total:\n{altura_total_cm} cm', 
                va='center', ha='left', fontsize=12, fontweight='bold')
        
        if tipo_relleno == "Un solo relleno general":
            ax.text(50, 20 + altura_total_dibujo + 5, f'Relleno: {relleno_global}', 
                    va='bottom', ha='center', fontsize=11, fontstyle='italic', color='dimgray')
                
    else:
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        
        if tipo_relleno == "Un solo relleno general":
            ax.text(50, 95, f'Relleno General: {relleno_global}', 
                    va='top', ha='center', fontsize=11, fontstyle='italic', color='dimgray')

        for i, piso in enumerate(pisos_agrupados):
            medida = piso['medida']
            largo_str, ancho_str = medida.replace(" cm", "").split("x")
            largo, ancho = int(largo_str), int(ancho_str)
            
            escala = 1.3
            dibujo_largo = largo * escala
            dibujo_ancho = ancho * escala
            
            x_inicio = 50 - (dibujo_largo / 2)
            y_inicio = 50 - (dibujo_ancho / 2)
            
            color_fondo = 'seashell' if i % 2 == 0 else 'oldlace'
            
            plancha = patches.Rectangle((x_inicio, y_inicio), dibujo_largo, dibujo_ancho, 
                                        linewidth=2, edgecolor='black', facecolor=color_fondo)
            ax.add_patch(plancha)
            
            pos_y_texto = y_inicio + dibujo_ancho - 8 - (i * 12)
            
            etiqueta = f"{medida}\nAltura fija: 12 cm"
            if tipo_relleno == "Rellenos diferentes por base":
                etiqueta += f"\nRelleno: {piso['relleno']}"
                
            ax.text(50, pos_y_texto, etiqueta, va='top', ha='center', fontsize=9, 
                    fontweight='bold', color='black', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=2))

    return fig

# --- FUNCIÓN REINICIAR Y RESET ---
def reiniciar_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.bases_confirmadas = False

def reset_confirmacion():
    st.session_state.bases_confirmadas = False

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Creador de Pasteles", layout="centered")

# Estilo para forzar el botón Aceptar a verde
st.markdown("""
    <style>
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #28a745; 
        color: white; 
        border-color: #28a745;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #218838; 
        border-color: #1e7e34;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎂 Creador de Pasteles")
st.write("Selecciona los parámetros y el sistema calculará las porciones y armará el diseño.")
st.divider()

# --- 1. DATOS PRINCIPALES ---
tipo = st.selectbox("1. Tipo de Pastel:", ["Tipo Base (Redondo)", "Tipo Plancha (Rectangular)"], index=None, placeholder="Selecciona el tipo...", key="in_tipo", on_change=reset_confirmacion)

st.write("**2. Configuración de Rellenos:**")
tipo_relleno = st.radio("¿El pastel lleva el mismo relleno en todas las bases?", 
                        ["Un solo relleno general", "Rellenos diferentes por base"], index=None, on_change=reset_confirmacion)

relleno_global = ""
if tipo_relleno == "Un solo relleno general":
    relleno_global = st.text_input("Relleno para todo el pastel:", value="", placeholder="Ej. Fresa con Crema", key="in_relleno_global", on_change=reset_confirmacion)

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

if "bases_confirmadas" not in st.session_state:
    st.session_state.bases_confirmadas = False

num_bases = st.number_input("3. ¿Cuántos pasteles (bases de 6cm) vas a agregar?", min_value=1, max_value=6, value=None, placeholder="Ej. 2", key="in_bases", on_change=reset_confirmacion)

bases_ingresadas = []

if num_bases is not None and tipo is not None and tipo_relleno is not None:
    
    # El botón Aceptar siempre visible en este punto
    if st.button("✅ Aceptar", type="primary"):
        st.session_state.bases_confirmadas = True

    # Se despliega el menú solo tras confirmar
    if st.session_state.bases_confirmadas:
        st.write("**Selecciona la medida de cada base agregada:**")
        if tipo == "Tipo Base (Redondo)":
            st.info("💡 Tip: Bases de la misma medida se fusionan en pisos de altura doble (12 cm).")
        
        capacidad_temporal = 0
        
        for i in range(num_bases):
            # Lógica para ocultar los rellenos si es "Un solo relleno"
            if tipo_relleno == "Rellenos diferentes por base":
                col1, col2 = st.columns(2)
                with col1:
                    # El format_func es lo que permite mostrar la capacidad en la lista desplegable
                    dim = st.selectbox(f"Medida Base {i+1}", opciones_medidas, index=None, placeholder="Medida...", 
                                       format_func=lambda x: f"{x} ({diccionario_actual[x]} pers.)", key=f"in_dim_{i}")
                with col2:
                    rell = st.text_input(f"Relleno Base {i+1}", value="", placeholder="Ej. Chocolate", key=f"in_rell_{i}")
            else:
                # Se oculta el text_input completamente, solo queda la lista desplegable a lo ancho
                dim = st.selectbox(f"Medida Base {i+1}", opciones_medidas, index=None, placeholder="Selecciona medida...", 
                                   format_func=lambda x: f"{x} ({diccionario_actual[x]} pers.)", key=f"in_dim_{i}")
                rell = relleno_global
                    
            bases_ingresadas.append({'medida': dim, 'relleno': rell})
            
            # Contador de personas en vivo
            if dim is not None:
                capacidad_temporal += diccionario_actual[dim]

        # Texto dinámico mostrando la capacidad
        if capacidad_temporal > 0:
            st.success(f"👥 Capacidad seleccionada hasta ahora: **{capacidad_temporal} personas**")

        st.divider()

        if "calculado" not in st.session_state:
            st.session_state.calculado = False

        # --- 3. BOTÓN DE CALCULAR ---
        if st.button("🚀 Calcular y Generar Esquema"):
            
            campos_incompletos = False
            for b in bases_ingresadas:
                if b['medida'] is None or b['relleno'] == "":
                    campos_incompletos = True

            if campos_incompletos:
                st.error("⚠️ Por favor, llena todos los campos y selecciona las medidas antes de calcular.")
            else:
                with st.spinner('Ensamblando el pastel y calculando porciones...'):
                    time.sleep(1.5) 
                
                st.session_state.total_personas = sum([diccionario_actual[b['medida']] for b in bases_ingresadas])
                st.session_state.pisos_agrupados = agrupar_pisos(bases_ingresadas)
                
                if tipo == "Tipo Plancha (Rectangular)":
                    st.session_state.altura_total = 12 
                else:
                    st.session_state.altura_total = sum([piso['altura_cm'] for piso in st.session_state.pisos_agrupados])
                    
                st.session_state.tipo_guardado = tipo
                st.session_state.num_bases_guardado = num_bases
                st.session_state.tipo_relleno_guardado = tipo_relleno
                st.session_state.relleno_global_guardado = relleno_global
                st.session_state.calculado = True

        # --- MOSTRAR RESULTADOS SI YA SE CALCULÓ ---
        if st.session_state.get('calculado', False):
            st.success("¡Esquema generado con éxito!")
            
            st.subheader("📊 Resumen del Pedido")
            st.write(f"👥 **Capacidad total:** Alcanza para **{st.session_state.total_personas} personas**.")
            st.write(f"🥞 **Total de bases:** {st.session_state.num_bases_guardado}")
            st.write(f"🍰 **Pisos resultantes (visibles):** {len(st.session_state.pisos_agrupados)}")
            st.write(f"📏 **Altura total:** {st.session_state.altura_total} cm")

            st.subheader("📐 Esquema Visual")
            fig = dibujar_esquema(st.session_state.pisos_agrupados, st.session_state.tipo_guardado, st.session_state.tipo_relleno_guardado, st.session_state.relleno_global_guardado)
            st.pyplot(fig)
            
            buf = io.BytesIO()
            fig.savefig(buf, format="jpeg", bbox_inches='tight')
            buf.seek(0)
            
            texto_wa = f"*Resumen de Pedido de Pastel*\n\n"
            texto_wa += f"• *Tipo:* {st.session_state.tipo_guardado}\n"
            texto_wa += f"• *Bases totales:* {st.session_state.num_bases_guardado}\n"
            texto_wa += f"• *Altura Total:* {st.session_state.altura_total} cm\n\n"
            texto_wa += f"📊 *Distribución y Rellenos:*\n"
            if st.session_state.tipo_relleno_guardado == "Un solo relleno general":
                texto_wa += f"  - Relleno General: {st.session_state.relleno_global_guardado}\n"
            for p in st.session_state.pisos_agrupados:
                rell_texto = "" if st.session_state.tipo_relleno_guardado == "Un solo relleno general" else f" | Relleno: {p['relleno']}"
                texto_wa += f"  - {p['medida']} | {p['altura_cm']} cm{rell_texto}\n"
            texto_wa += f"\n👥 *Capacidad Calculada:* ¡Para {st.session_state.total_personas} personas!\n\n"
            texto_wa += f"Te adjunto en un momento el diseño visual del pastel."
            
            texto_wa_encoded = urllib.parse.quote(texto_wa)
            whatsapp_url = f"https://wa.me/522281342454?text={texto_wa_encoded}"
            
            col_down, col_wa = st.columns(2)
            with col_down:
                st.download_button(
                    label="💾 Descargar Diagrama (JPG)",
                    data=buf,
                    file_name="esquema_pastel.jpg",
                    mime="image/jpeg",
                    use_container_width=True
                )
            with col_wa:
                st.link_button("💬 Enviar por WhatsApp", whatsapp_url, use_container_width=True)

# --- BOTÓN BORRAR TODO (HASTA ABAJO) ---
st.write("")
st.write("")
st.divider()
st.button("🗑️ Borrar Todo y Limpiar Campos", on_click=reiniciar_app, use_container_width=True)
