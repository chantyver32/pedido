import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

# --- DICCIONARIOS INVERTIDOS ---
# Ahora buscamos por medida para obtener la capacidad de personas
capacidades_base = {
    "15 cm": 6,
    "20 cm": 15,
    "25 cm": 25,
    "30 cm": 40,
    "35 cm": 60,
    "40 cm": 80,
    "45 cm": 100,
    "50 cm": 120
}

capacidades_plancha = {
    "31x21 cm": 40,
    "36x28 cm": 60,
    "41x30 cm": 80,
    "54x37 cm": 100,
    "63x37 cm": 120
}

# --- FUNCIONES DE LÓGICA Y DIBUJO ---
def extraer_ancho(medida_str):
    # Extrae el primer número de la medida para poder ordenarlos de mayor a menor
    if "x" in medida_str:
        return int(medida_str.split("x")[0])
    return int(medida_str.split()[0])

def agrupar_pisos(dimensiones):
    # Ordena de mayor a menor ancho
    dimensiones_ordenadas = sorted(dimensiones, key=extraer_ancho, reverse=True)
    pisos = []
    
    # Agrupa medidas iguales en pisos de mayor altura
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
    
    # Dibujar de abajo hacia arriba
    for i, piso in enumerate(pisos_agrupados):
        medida = piso['medida']
        altura_cm = piso['altura_cm']
        
        # Calcular proporciones visuales
        ancho_real = extraer_ancho(medida)
        ancho_dibujo = ancho_real * 1.5 # Escala visual para el ancho
        altura_dibujo = altura_cm * 2.5 # Escala visual para la altura
        x_inicio = 50 - (ancho_dibujo / 2)
        
        pastel = patches.Rectangle((x_inicio, y_inicio), ancho_dibujo, altura_dibujo, 
                                   linewidth=2, edgecolor='black', facecolor='seashell')
        ax.add_patch(pastel)
        
        # Etiqueta de la medida del diámetro/ancho (Centro del piso)
        etiqueta_ancho = f"{medida} dia." if tipo == "Tipo Base (Redondo)" else medida
        ax.text(50, y_inicio + (altura_dibujo/2), etiqueta_ancho, 
                va='center', ha='center', fontsize=10, fontweight='bold', color='black')
        
        # Etiqueta de la altura del piso (Izquierda)
        ax.text(x_inicio - 2, y_inicio + (altura_dibujo/2), f"{altura_cm} cm\n({piso['cantidad_bases']} bases)", 
                va='center', ha='right', fontsize=9, color='blue')
        
        y_inicio += altura_dibujo
        altura_total_dibujo += altura_dibujo
        altura_total_cm += altura_cm
        
    # Cota de altura total (Derecha)
    ax.annotate('', xy=(88, 20), xytext=(88, 20 + altura_total_dibujo),
                arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5))
    ax.text(91, 20 + altura_total_dibujo/2, f'Total:\n{altura_total_cm} cm', 
            va='center', ha='left', fontsize=12, fontweight='bold')
    
    # Texto de Relleno
    ax.text(50, y_inicio + 8, f'Relleno: {relleno}', va='center', ha='center', 
            fontsize=11, fontstyle='italic', color='dimgray')
    
    return fig

# --- FUNCIÓN PARA BORRAR TODO ---
def reiniciar_app():
    for key in st.session_state.keys():
        del st.session_state[key]

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Creador de Pasteles", layout="centered")

col_titulo, col_boton = st.columns([3, 1])
with col_titulo:
    st.title("🎂 Creador de Pasteles")
with col_boton:
    st.write("") 
    st.button("🗑️ Borrar Todo", on_click=reiniciar_app, type="secondary")

st.write("Selecciona los diámetros y el sistema calculará las porciones y armará el diseño.")
st.divider()

# --- 1. DATOS PRINCIPALES ---
tipo = st.selectbox("1. Tipo de Pastel:", ["Tipo Base (Redondo)", "Tipo Plancha (Rectangular)"], index=None, placeholder="Selecciona el tipo...", key="in_tipo")
relleno = st.text_input("2. Relleno:", value="", placeholder="Ej. Fresa con Crema", key="in_relleno")

# Opciones de medidas basadas en el tipo de pastel seleccionado
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

# --- 3. BOTÓN DE CALCULAR ---
if st.button("🚀 Calcular y Generar Esquema", type="primary"):
    
    if tipo is None or not relleno or num_bases is None or None in dimensiones_ingresadas:
        st.error("⚠️ Por favor, llena todos los campos y selecciona la medida de todas las bases antes de calcular.")
    else:
        with st.spinner('Ensamblando el pastel y calculando porciones...'):
            time.sleep(1.5) 
        
        # Cálculos Matemáticos
        total_personas = sum([diccionario_actual[dim] for dim in dimensiones_ingresadas])
        pisos_agrupados = agrupar_pisos(dimensiones_ingresadas)
        altura_total = sum([piso['altura_cm'] for piso in pisos_agrupados])

        st.success("¡Esquema generado con éxito!")
        
        # Resumen
        st.subheader("📊 Resumen del Pedido")
        st.write(f"👥 **Capacidad total:** Alcanza para **{total_personas} personas**.")
        st.write(f"🥞 **Total de bases (6cm c/u):** {num_bases}")
        st.write(f"🍰 **Pisos resultantes (visibles):** {len(pisos_agrupados)}")
        st.write(f"📏 **Altura total:** {altura_total} cm")

        # Visual
        st.subheader("📐 Esquema Visual")
        fig = dibujar_esquema(pisos_agrupados, relleno, tipo)
        st.pyplot(fig)
