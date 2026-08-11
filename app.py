import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import io

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Inventario Champlitte", layout="centered")

# --- INICIALIZAR MEMORIA (BASE DE DATOS TEMPORAL) ---
if 'pendientes_venta' not in st.session_state:
    # Agregamos un par de datos de ejemplo basados en tu imagen para que no se vea vacío
    st.session_state.pendientes_venta = [
        ["Pastel Macadamia Chico", "LÍNEA C", 1, "2026-08-13"],
        ["Pastel Milkyway Chico", "LÍNEA C", 2, "2026-08-16"]
    ]

# --- FUNCIÓN PARA DIBUJAR LA IMAGEN DE LA TABLA ---
def generar_imagen_pendientes(datos_venta, total_pasteles):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Obtener fecha y hora actual para el subtítulo
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Título y Subtítulo
    plt.text(0.5, 1.15, "FALTA POR VENDER", fontsize=24, fontweight='bold', ha='center', color='#4A151C')
    plt.text(0.5, 1.05, f"🗓️ ACTUALIZADO AL {ahora}", fontsize=12, ha='center', color='#707070')
    
    # Columnas de la tabla
    columnas = ["PRODUCTO", "LÍNEA", "CANTIDAD\nPOR VENDER", "FECHA"]
    
    # Crear la tabla
    tabla = ax.table(cellText=datos_venta, colLabels=columnas, loc='center', cellLoc='center')
    
    # Estilos de la tabla
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(11)
    tabla.scale(1, 2.5) 
    
    # Pintar celdas
    for (fila, col), celda in tabla.get_celld().items():
        if fila == 0:
            celda.set_text_props(weight='bold', color='white')
            celda.set_facecolor('#8A1C31') 
        else:
            if fila % 2 == 0:
                celda.set_facecolor('#FDF4F5')
            else:
                celda.set_facecolor('#FFFFFF')
            
            if col == 0: 
                celda.set_text_props(ha='left')
            elif col == 1: 
                celda.set_text_props(weight='bold', color='#D96A6A')
            elif col == 2: 
                celda.set_text_props(weight='bold', size=14)
                
    # Total de productos en la parte inferior
    plt.text(0.4, -0.1, "TOTAL DE PRODUCTOS\nPOR VENDER", fontsize=11, fontweight='bold', ha='right', color='#8A1C31')
    plt.text(0.6, -0.1, f"{total_pasteles}\nPASTELES", fontsize=14, fontweight='bold', ha='center', color='white', 
             bbox=dict(facecolor='#8A1C31', edgecolor='none', boxstyle='round,pad=0.5'))

    # Guardar la imagen en memoria para mostrarla/descargarla
    buf = io.BytesIO()
    plt.savefig(buf, format='jpg', bbox_inches='tight', dpi=300)
    buf.seek(0)
    return buf

# --- INTERFAZ PRINCIPAL ---
st.title("🍰 Sistema de Ventas Champlitte")
st.divider()

# Creación de las dos pestañas que pediste
tab1, tab2 = st.tabs(["📝 Agregar Pastel", "📊 Pendientes para Venta"])

# --- PESTAÑA 1: AGREGAR (CON AUTO-LIMPIEZA) ---
with tab1:
    st.subheader("Registrar nuevo producto")
    st.write("Llena los datos. Al guardar, los campos volverán a quedar en blanco automáticamente.")
    
    # La magia para que no tengas que borrar a mano está en este "clear_on_submit=True"
    with st.form("form_agregar", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            producto_in = st.text_input("Nombre del Producto", placeholder="Ej. Pastel Macadamia Chico")
            linea_in = st.selectbox("Línea", ["LÍNEA C", "LÍNEA G"], index=None, placeholder="Selecciona...")
        
        with col2:
            cantidad_in = st.number_input("Cantidad por Vender", min_value=1, step=1)
            fecha_in = st.date_input("Fecha de entrega/registro")
            
        submit_btn = st.form_submit_button("➕ Agregar a la Lista", type="primary")
        
        if submit_btn:
            if producto_in and linea_in:
                # Convertimos la fecha a texto para la tabla
                fecha_str = fecha_in.strftime("%Y-%m-%d")
                # Guardamos en la memoria
                st.session_state.pendientes_venta.append([producto_in, linea_in, cantidad_in, fecha_str])
                st.success(f"¡'{producto_in}' agregado con éxito! El formulario ya está limpio.")
            else:
                st.error("Por favor, llena al menos el Producto y la Línea.")

# --- PESTAÑA 2: MOSTRAR Y GENERAR IMAGEN ---
with tab2:
    st.subheader("Lista de Pendientes")
    
    if len(st.session_state.pendientes_venta) == 0:
        st.info("No hay pasteles pendientes de venta.")
    else:
        # Calcular el total sumando la columna de cantidad (índice 2)
        total_pasteles = sum([item[2] for item in st.session_state.pendientes_venta])
        
        # Mostrar los datos crudos en Streamlit
        st.dataframe(
            st.session_state.pendientes_venta, 
            column_config={
                "0": "Producto", "1": "Línea", "2": "Cantidad", "3": "Fecha"
            },
            use_container_width=True
        )
        
        st.divider()
        st.write("### 🖼️ Imagen Generada Automáticamente")
        
        # Aquí llamamos a la función que crea la imagen usando los datos de la sesión
        img_buffer = generar_imagen_pendientes(st.session_state.pendientes_venta, total_pasteles)
        
        # Mostramos la imagen
        st.image(img_buffer, use_column_width=True)
        
        # Botón para descargar
        st.download_button(
            label="💾 Descargar Imagen",
            data=img_buffer,
            file_name=f"Falta_Por_Vender_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
        
        # Botón extra para vaciar la lista si ya vendiste todo
        st.divider()
        if st.button("🗑️ Borrar todo el historial y empezar de cero"):
            st.session_state.pendientes_venta = []
            st.rerun()
