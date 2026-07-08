import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import time

# --- DICCIONARIOS DE MEDIDAS (Basados en la Imagen 1) ---
medidas_base = {
    6: 15,
    15: 20,
    25: 25,
    40: 30,
    60: 35,
    80: 40,
    100: 45,
    120: 50
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

# Modificamos la función para que reciba una lista de alturas en lugar de un solo número
def dibujar_esquema(ancho_texto, alturas_cm, relleno, tipo):
    fig, ax = plt.subplots(figsize=(6, 7))
    
    # Configuraciones visuales base
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 130) # Aumentamos un poco el límite vertical por si hay muchos pisos
    ax.axis('off')
    
    # Dibujar la base del pastel (Plato)
    plato = patches.Ellipse((50, 20), 80, 10, color='saddlebrown')
    ax.add_patch(plato)
    
    # Variables para el dibujo dinámico
    ancho_dibujo = 60
    y_inicio = 20
    altura_total_dibujo = 0
    
    # Dibujar cada piso con su altura específica
    for i, h_cm in enumerate(alturas_cm):
        reduccion = i * 10 if tipo == "Tipo Base (Redondo)" else 0
        ancho_actual = ancho_dibujo - reduccion
        x_inicio = 50 - (ancho_actual / 2)
        
        # Escalar la altura real (cm) a unidades de dibujo (1 cm = 2.5 unidades visuales)
        altura_dibujo = h_cm * 2.5
        
        pastel = patches.Rectangle((x_inicio, y_inicio), ancho_actual, altura_dibujo, 
                                   linewidth=2, edgecolor='black', facecolor='seashell')
        ax.add_patch(pastel)
        
        # Etiqueta individual para cada piso a la izquierda
        ax.text(x_inicio - 2, y_inicio + (altura_dibujo/2), f'{h_cm} cm', 
                va='center', ha='right', fontsize=9, color='blue')
        
        y_inicio += altura_dibujo
        altura_total_dibujo += altura_dibujo
        
    # --- Añadir las Cotas Generales ---
    altura_total_cm = sum(alturas_cm)
    
    # Cota de altura total (Derecha)
    ax.annotate('', xy=(85, 20), xytext=(85, 20 + altura_total_dibujo),
                arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5))
    ax.text(88, 20 + altura_total_dibujo/2, f'Total:\n{altura_total_cm} cm', 
            va='center', ha='left', fontsize=12, fontweight='bold')
    
    # Cota de ancho/diámetro (Abajo)
    ax.annotate('', xy=(50 - ancho_dibujo/2, 10), xytext=(50 + ancho_dibujo/2, 10),
                arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5))
    etiqueta_ancho = f'{ancho_texto} dia.' if tipo == "Tipo Base (Redondo)" else ancho_texto
    ax.text(50, 4, etiqueta_ancho, va='center', ha='center', fontsize=12, fontweight='bold')
    
    # Texto de Relleno (Hasta arriba)
    ax.text(50, y_inicio + 8, f'Relleno: {relleno}', va='center', ha='center', 
            fontsize=11, fontstyle='italic', color='dimgray')
    
    return fig

# --- INTERFAZ DE USUARIO CON STREAMLIT ---
st.set_page_config(page_title="Cotizador de Pasteles", layout="centered")
st.title("🎂 Generador de Medidas de Pasteles")
st.write("Configura el pastel piso por piso.")

# Usamos st.session_state para recordar cuántos pisos llevamos agregados
if 'num_pisos' not in st.session_state:
    st.session_state.num_pisos = 1

# Controles Base
col1, col2 = st.columns(2)
with col1:
    personas = st.number_input("Número de personas:", min_value=1, max_value=120, value=30, step=1)
with col2:
    tipo = st.selectbox("Tipo de Pastel:", ["Tipo Base (Redondo)", "Tipo Plancha (Rectangular)"])

relleno = st.text_input("Relleno:", value="Fresa con Crema")

st.divider()

# --- SECCIÓN DINÁMICA DE PISOS ---
st.subheader("🍰 Configuración de Pisos")

# Botón para agregar un piso extra
if st.button("➕ Agregar Piso"):
    st.session_state.num_pisos += 1

# Botón para quitar el último piso (por si nos equivocamos)
if st.session_state.num_pisos > 1:
    if st.button("➖ Quitar último piso"):
        st.session_state.num_pisos -= 1

# Generar un input de número por cada piso que tengamos en memoria
alturas_ingresadas = []
for i in range(st.session_state.num_pisos):
    h = st.number_input(f"Altura del Piso {i+1} (cm):", min_value=1, value=6, key=f"piso_{i}")
    alturas_ingresadas.append(h)

st.divider()

# --- BOTÓN DE CALCULAR Y ANIMACIÓN ---
if st.button("🚀 Calcular y Generar Esquema", type="primary"):
    
    # Animación de carga
    with st.spinner('Procesando medidas y dibujando el esquema...'):
        time.sleep(1.5) # Pausa de 1.5 segundos para la animación
    
    # Cálculos
    altura_total = sum(alturas_ingresadas)
    medida_calculada, cap_max = obtener_medida(personas, tipo)

    # Mostrar Resultados
    st.success("¡Esquema generado con éxito!")
    
    st.subheader("📊 Resumen del Pedido")
    st.write(f"**Capacidad calculada:** Hasta {cap_max} personas.")
    
    if tipo == "Tipo Base (Redondo)":
        st.write(f"**Diámetro requerido:** {medida_calculada} cm")
    else:
        st.write(f"**Medidas requeridas:** {medida_calculada}")
        
    st.write(f"**Pisos totales:** {st.session_state.num_pisos}")
    st.write(f"**Altura total:** {altura_total} cm")

    # Generar y mostrar imagen
    st.subheader("📐 Esquema Visual")
    fig = dibujar_esquema(medida_calculada, alturas_ingresadas, relleno, tipo)
    st.pyplot(fig)
