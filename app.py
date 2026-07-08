import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

# --- DICCIONARIOS DE MEDIDAS ---
medidas_base = {
    6: 15, 15: 20, 25: 25, 40: 30,
    60: 35, 80: 40, 100: 45, 120: 50
}

medidas_plancha = {
    40: ("31x21 cm", "0.500 kg"),
    60: ("36x28 cm", "0.750 kg"),
    80: ("41x30 cm", "1 kg"),
    100: ("54x37 cm", "1.250 kg"),
    120: ("63x37 cm", "1.500 kg")
}

def obtener_medida(personas, tipo):
    if tipo == "Tipo Base (Redondo)":
        for cap, diametro in sorted(medidas_base.items()):
            if personas <= cap:
                return diametro, cap
        return 50, 120 
    else:
        for cap, datos in sorted(medidas_plancha.items()):
            if personas <= cap:
                return datos[0], cap
        return "63x37 cm", 120 

def dibujar_esquema(ancho_texto, alturas_cm, relleno, tipo):
    fig, ax = plt.subplots(figsize=(6, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 130) 
    ax.axis('off')
    
    plato = patches.Ellipse((50, 20), 80, 10, color='saddlebrown')
    ax.add_patch(plato)
    
    ancho_dibujo = 60
    y_inicio = 20
    altura_total_dibujo = 0
    
    for i, h_cm in enumerate(alturas_cm):
        reduccion = i * 10 if tipo == "Tipo Base (Redondo)" else 0
        ancho_actual = ancho_dibujo - reduccion
        x_inicio = 50 - (ancho_actual / 2)
        
        altura_dibujo = h_cm * 2.5
        
        pastel = patches.Rectangle((x_inicio, y_inicio), ancho_actual, altura_dibujo, 
                                   linewidth=2, edgecolor='black', facecolor='seashell')
        ax.add_patch(pastel)
        
        ax.text(x_inicio - 2, y_inicio + (altura_dibujo/2), f'{h_cm} cm', 
                va='center', ha='right', fontsize=9, color='blue')
        
        y_inicio += altura_dibujo
        altura_total_dibujo += altura_dibujo
        
    altura_total_cm = sum(alturas_cm)
    
    ax.annotate('', xy=(85, 20), xytext=(85, 20 + altura_total_dibujo),
                arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5))
    ax.text(88, 20 + altura_total_dibujo/2, f'Total:\n{altura_total_cm} cm', 
            va='center', ha='left', fontsize=12, fontweight='bold')
    
    ax.annotate('', xy=(50 - ancho_dibujo/2, 10), xytext=(50 + ancho_dibujo/2, 10),
                arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5))
    etiqueta_ancho = f'{ancho_texto} dia.' if tipo == "Tipo Base (Redondo)" else ancho_texto
    ax.text(50, 4, etiqueta_ancho, va='center', ha='center', fontsize=12, fontweight='bold')
    
    ax.text(50, y_inicio + 8, f'Relleno: {relleno}', va='center', ha='center', 
            fontsize=11, fontstyle='italic', color='dimgray')
    
    return fig

# --- FUNCIÓN PARA BORRAR TODO ---
def reiniciar_app():
    # Elimina todas las variables guardadas en la sesión actual
    for key in st.session_state.keys():
        del st.session_state[key]

# --- INTERFAZ DE USUARIO CON STREAMLIT ---
st.set_page_config(page_title="Cotizador de Pasteles", layout="centered")

# Encabezado y botón de reinicio
col_titulo, col_boton = st.columns([3, 1])
with col_titulo:
    st.title("🎂 Creador de Pasteles")
with col_boton:
    st.write("") # Espaciador
    st.button("🗑️ Borrar Todo", on_click=reiniciar_app, type="secondary")

st.write("Completa los datos en orden para generar el diseño.")
st.divider()

# --- 1. DATOS PRINCIPALES ---
# Usamos index=None y value=None para que todo empiece en blanco
personas = st.number_input("1. Número de personas:", min_value=1, max_value=120, value=None, placeholder="Ej. 50", key="in_personas")
tipo = st.selectbox("2. Tipo de Pastel:", ["Tipo Base (Redondo)", "Tipo Plancha (Rectangular)"], index=None, placeholder="Selecciona el tipo...", key="in_tipo")
relleno = st.text_input("3. Relleno:", value="", placeholder="Ej. Fresa con Crema", key="in_relleno")

# --- 2. CONFIGURACIÓN DE PISOS ---
st.divider()
num_pisos = st.selectbox("4. ¿Cuántos pisos tendrá el pastel?", [1, 2, 3], index=None, placeholder="Elige 1, 2 o 3...", key="in_pisos")

alturas_ingresadas = []

# Mostrar las entradas de altura SOLO si el usuario ya eligió cuántos pisos quiere
if num_pisos is not None:
    st.write("**Ingresa la altura para cada piso (en cm):**")
    cols_pisos = st.columns(num_pisos)
    
    for i in range(num_pisos):
        with cols_pisos[i]:
            h = st.number_input(f"Piso {i+1}", min_value=1, value=None, placeholder="cm", key=f"in_h_{i}")
            alturas_ingresadas.append(h)

st.divider()

# --- 3. BOTÓN DE CALCULAR Y ANIMACIÓN ---
if st.button("🚀 Calcular y Generar Esquema", type="primary"):
    
    # Validación: Comprobar que no haya campos vacíos (None o "")
    if personas is None or tipo is None or not relleno or num_pisos is None or None in alturas_ingresadas:
        st.error("⚠️ Por favor, llena todos los campos, incluyendo las alturas de los pisos, antes de calcular.")
    else:
        # Animación de carga
        with st.spinner('Procesando medidas y dibujando el esquema...'):
            time.sleep(1.5) 
        
        # Cálculos
        altura_total = sum(alturas_ingresadas)
        medida_calculada, cap_max = obtener_medida(personas, tipo)

        # Mostrar Resultados
        st.success("¡Esquema generado con éxito!")
        
        st.subheader("📊 Resumen del Pedido")
        st.write(f"**Capacidad:** Hasta {cap_max} personas.")
        
        if tipo == "Tipo Base (Redondo)":
            st.write(f"**Diámetro requerido:** {medida_calculada} cm")
        else:
            st.write(f"**Medidas requeridas:** {medida_calculada}")
            
        st.write(f"**Pisos totales:** {num_pisos}")
        st.write(f"**Altura total:** {altura_total} cm")

        # Generar y mostrar imagen
        st.subheader("📐 Esquema Visual")
        fig = dibujar_esquema(medida_calculada, alturas_ingresadas, relleno, tipo)
        st.pyplot(fig)
