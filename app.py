import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- DICCIONARIOS DE MEDIDAS (Basados en la Imagen 1) ---
# Formato: Personas -> Diametro en cm
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

# Formato: Max Personas -> (Largo x Ancho, Peso)
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
        return 50, 120 # Máximo por defecto
    else:
        for cap, datos in sorted(medidas_plancha.items()):
            if personas <= cap:
                return datos[0], cap
        return "63x37 cm", 120 # Máximo por defecto

def dibujar_esquema(ancho_texto, altura_cm, niveles, relleno, tipo):
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Configuraciones visuales base
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Dibujar la base del pastel (Plato)
    plato = patches.Ellipse((50, 20), 80, 10, color='saddlebrown')
    ax.add_patch(plato)
    
    # Dibujar los niveles del pastel
    ancho_dibujo = 60
    altura_dibujo_por_nivel = 15
    y_inicio = 20
    
    for i in range(niveles):
        # Cada nivel se hace un poco más angosto si es redondo para simular pisos
        reduccion = i * 10 if tipo == "Tipo Base (Redondo)" else 0
        ancho_actual = ancho_dibujo - reduccion
        x_inicio = 50 - (ancho_actual / 2)
        
        pastel = patches.Rectangle((x_inicio, y_inicio), ancho_actual, altura_dibujo_por_nivel, 
                                   linewidth=2, edgecolor='black', facecolor='seashell')
        ax.add_patch(pastel)
        y_inicio += altura_dibujo_por_nivel
        
    # --- Añadir las Cotas (Líneas de medida) ---
    # Cota de altura (Derecha)
    ax.annotate('', xy=(85, 20), xytext=(85, 20 + (niveles * altura_dibujo_por_nivel)),
                arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5))
    ax.text(88, 20 + (niveles * altura_dibujo_por_nivel)/2, f'{altura_cm} cm', 
            va='center', ha='left', fontsize=12, fontweight='bold')
    
    # Cota de ancho/diámetro (Abajo)
    ax.annotate('', xy=(50 - ancho_dibujo/2, 10), xytext=(50 + ancho_dibujo/2, 10),
                arrowprops=dict(arrowstyle='|-|', color='black', lw=1.5))
    etiqueta_ancho = f'{ancho_texto} dia.' if tipo == "Tipo Base (Redondo)" else ancho_texto
    ax.text(50, 4, etiqueta_ancho, va='center', ha='center', fontsize=12, fontweight='bold')
    
    # Texto de Relleno
    ax.text(50, y_inicio + 5, f'Relleno: {relleno}', va='center', ha='center', 
            fontsize=11, fontstyle='italic', color='dimgray')
    
    return fig

# --- INTERFAZ DE USUARIO CON STREAMLIT ---
st.set_page_config(page_title="Cotizador de Pasteles", layout="centered")
st.title("🎂 Generador de Medidas de Pasteles")
st.write("Ingresa los datos del cliente para calcular las medidas y generar el esquema visual.")

# Controles de Entrada
col1, col2 = st.columns(2)

with col1:
    personas = st.number_input("Número de personas:", min_value=1, max_value=120, value=30, step=1)
    tipo = st.selectbox("Tipo de Pastel:", ["Tipo Base (Redondo)", "Tipo Plancha (Rectangular)"])

with col2:
    niveles = st.selectbox("Altura (Niveles):", [1, 2, 3], format_func=lambda x: f"{x} Nivel(es) - {x*6} cm")
    relleno = st.text_input("Relleno:", value="Fresa con Crema")

st.divider()

# Cálculos
altura_total = niveles * 6
medida_calculada, cap_max = obtener_medida(personas, tipo)

# Mostrar Resultados
st.subheader("📊 Resumen del Pedido")
st.write(f"**Capacidad calculada:** Hasta {cap_max} personas.")
if tipo == "Tipo Base (Redondo)":
    st.write(f"**Diámetro requerido:** {medida_calculada} cm")
else:
    st.write(f"**Medidas requeridas:** {medida_calculada}")
st.write(f"**Altura total:** {altura_total} cm")

# Generar y mostrar imagen
st.subheader("📐 Esquema Visual")
fig = dibujar_esquema(medida_calculada, altura_total, niveles, relleno, tipo)
st.pyplot(fig)