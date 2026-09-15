# Insertar imagen bajo el título
try:
  imagen_cabecera = Image.open("Profesor_ingles.jpg")
  # Se cambió use_column_width por use_container_width
  st.image(
      imagen_cabecera,
      use_container_width=True,
      caption="Análisis de tono y subjetividad académica",
  )
except FileNotFoundError:
  st.info(
      "🖼️ *Coloca una imagen llamada 'Profesor_ingles.jpg' en la carpeta para"
      " verla aquí.*"
  )
