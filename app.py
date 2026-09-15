import re
from googletrans import Translator
import pandas as pd
from PIL import Image
import streamlit as st
from textblob import TextBlob

# Configuración de la página
st.set_page_config(
    page_title="Essay Tone & Sentiment Auditor", page_icon="🎓", layout="wide"
)

# Estilos CSS personalizados para forzar MODO OSCURO elegante
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    div[data-baseweb="select"] > div {
        background-color: #161B22 !important;
        color: #ffffff !important;
    }
    textarea {
        background-color: #161B22 !important;
        color: #00FFC8 !important;
        border: 1px solid #30363D !important;
    }
    .stProgress > div > div > div > div {
        background-color: #00FFC8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- CABECERA Y TÍTULO ---
st.title("🎓 Auditor de Ensayos en Inglés para amigos")

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

st.markdown("""
Evalúa el **tono**, la **objetividad** y la **polaridad** de tu ensayo académico en un entorno visualmente descanso de noche.
""")

# Barra lateral en modo oscuro
st.sidebar.title("📌 Configuración")
modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:", ["Texto directo", "Archivo de texto"]
)

st.sidebar.info("""
**Criterios de Evaluación:**
- **Subjetividad < 0.40:** Ideal para Ensayos Argumentativos.
- **Subjetividad > 0.50:** Recomendado para Reflexiones Personales.
""")


# Función para contar palabras sin depender de NLTK
def contar_palabras(texto):
  stop_words = set([
      "a",
      "al",
      "algo",
      "algunas",
      "algunos",
      "ante",
      "antes",
      "como",
      "con",
      "contra",
      "cual",
      "cuando",
      "de",
      "del",
      "desde",
      "donde",
      "durante",
      "e",
      "el",
      "ella",
      "ellas",
      "ellos",
      "en",
      "entre",
      "era",
      "eras",
      "es",
      "esa",
      "esas",
      "ese",
      "eso",
      "esos",
      "esta",
      "estas",
      "este",
      "esto",
      "estos",
      "ha",
      "había",
      "han",
      "has",
      "hasta",
      "he",
      "la",
      "las",
      "le",
      "les",
      "lo",
      "los",
      "me",
      "mi",
      "mía",
      "mías",
      "mío",
      "míos",
      "mis",
      "mucho",
      "muchos",
      "muy",
      "nada",
      "ni",
      "no",
      "nos",
      "nosotras",
      "nosotros",
      "nuestra",
      "nuestras",
      "nuestro",
      "nuestros",
      "o",
      "os",
      "otra",
      "otras",
      "otro",
      "otros",
      "para",
      "pero",
      "poco",
      "por",
      "porque",
      "que",
      "quien",
      "quienes",
      "qué",
      "se",
      "sea",
      "sean",
      "según",
      "si",
      "sido",
      "sin",
      "sobre",
      "sois",
      "somos",
      "son",
      "soy",
      "su",
      "sus",
      "suya",
      "suyas",
      "suyo",
      "suyos",
      "también",
      "tanto",
      "te",
      "tenéis",
      "tenemos",
      "tener",
      "tengo",
      "ti",
      "tiene",
      "tienen",
      "todo",
      "todos",
      "tu",
      "tus",
      "tuya",
      "tuyas",
      "tuyo",
      "tuyos",
      "tú",
      "un",
      "una",
      "uno",
      "unos",
      "vosotras",
      "vosotros",
      "vuestra",
      "vuestras",
      "vuestro",
      "vuestros",
      "y",
      "ya",
      "yo",
      "about",
      "above",
      "after",
      "again",
      "against",
      "all",
      "am",
      "an",
      "and",
      "any",
      "are",
      "aren't",
      "as",
      "at",
      "be",
      "because",
      "been",
      "before",
      "being",
      "below",
      "between",
      "both",
      "but",
      "by",
      "can't",
      "cannot",
      "could",
      "couldn't",
      "did",
      "didn't",
      "do",
      "does",
      "doesn't",
      "doing",
      "don't",
      "down",
      "during",
      "each",
      "few",
      "for",
      "from",
      "further",
      "had",
      "hadn't",
      "has",
      "hasn't",
      "have",
      "haven't",
      "having",
      "he",
      "he'd",
      "he'll",
      "he's",
      "her",
      "here",
      "here's",
      "hers",
      "herself",
      "him",
      "himself",
      "his",
      "how",
      "how's",
      "i",
      "i'd",
      "i'll",
      "i'm",
      "i've",
      "if",
      "in",
      "into",
      "is",
      "isn't",
      "it",
      "it's",
      "its",
      "itself",
      "let's",
      "me",
      "more",
      "most",
      "mustn't",
      "my",
      "myself",
      "no",
      "nor",
      "not",
      "of",
      "off",
      "on",
      "once",
      "only",
      "or",
      "other",
      "ought",
      "our",
      "ours",
      "ourselves",
      "out",
      "over",
      "own",
      "same",
      "shan't",
      "she",
      "she'd",
      "she'll",
      "she's",
      "should",
      "shouldn't",
      "so",
      "some",
      "such",
      "than",
      "that",
      "that's",
      "the",
      "their",
      "theirs",
      "them",
      "themselves",
      "then",
      "there",
      "there's",
      "these",
      "they",
      "they'd",
      "they'll",
      "they're",
      "they've",
      "this",
      "those",
      "through",
      "to",
      "too",
      "under",
      "until",
      "up",
      "very",
      "was",
      "wasn't",
      "we",
      "we'd",
      "we'll",
      "we're",
      "we've",
      "were",
      "weren't",
      "what",
      "what's",
      "when",
      "when's",
      "where",
      "where's",
      "which",
      "while",
      "who",
      "who's",
      "whom",
      "why",
      "why's",
      "with",
      "would",
      "wouldn't",
      "you",
      "you'd",
      "you'll",
      "you're",
      "you've",
      "your",
      "yours",
      "yourself",
      "yourselves",
  ])

  palabras = re.findall(r"\b\w+\b", texto.lower())
  palabras_filtradas = [
      p for p in palabras if p not in stop_words and len(p) > 2
  ]

  contador = {}
  for palabra in palabras_filtradas:
    contador[palabra] = contador.get(palabra, 0) + 1

  return dict(
      sorted(contador.items(), key=lambda x: x[1], reverse=True)
  ), palabras_filtradas


translator = Translator()


def traducir_texto(texto):
  try:
    traduccion = translator.translate(texto, src="auto", dest="en")
    return traduccion.text
  except Exception:
    return texto


def procesar_texto(texto):
  texto_original = texto
  texto_ingles = traducir_texto(texto)

  blob = TextBlob(texto_ingles)
  sentimiento = blob.sentiment.polarity
  subjetividad = blob.sentiment.subjectivity

  frases_originales = [
      f.strip() for f in re.split(r"[.!?]+", texto_original) if f.strip()
  ]
  frases_traducidas = [
      f.strip() for f in re.split(r"[.!?]+", texto_ingles) if f.strip()
  ]

  frases_combinadas = []
  for i in range(min(len(frases_originales), len(frases_traducidas))):
    frases_combinadas.append({
        "original": frases_originales[i],
        "traducido": frases_traducidas[i],
    })

  contador_palabras, palabras = contar_palabras(texto_ingles)

  return {
      "sentimiento": sentimiento,
      "subjetividad": subjetividad,
      "frases": frases_combinadas,
      "contador_palabras": contador_palabras,
      "palabras": palabras,
      "texto_original": texto_original,
      "texto_traducido": texto_ingles,
  }


def crear_visualizaciones(resultados):
  col1, col2 = st.columns(2)

  with col1:
    st.subheader("📊 Diagnóstico del Tono Académico")

    st.write("**Nivel de Subjetividad / Juicio Personal:**")
    st.progress(resultados["subjetividad"])

    if resultados["subjetividad"] < 0.35:
      st.success(
          f"🎯 **Estilo Objetivo Académico** ({resultados['subjetividad']:.2f})"
      )
    elif resultados["subjetividad"] <= 0.60:
      st.warning(f"⚖️ **Tono Mixto** ({resultados['subjetividad']:.2f})")
    else:
      st.error(
          f"💭 **Alta Subjetividad** ({resultados['subjetividad']:.2f}) - Tono"
          " informal u opinión."
      )

    sentimiento_norm = (resultados["sentimiento"] + 1) / 2
    st.write("**Polaridad Emocional del Argumento:**")
    st.progress(sentimiento_norm)

  with col2:
    st.subheader("🔑 Vocabulario Frecuente")
    if resultados["contador_palabras"]:
      palabras_top = dict(list(resultados["contador_palabras"].items())[:8])
      st.bar_chart(palabras_top)

  st.divider()

  st.subheader("🔍 Desglose por Frase")
  if resultados["frases"]:
    for i, frase_dict in enumerate(resultados["frases"][:8], 1):
      st.markdown(
          f"**{i}. Original:** *\"{frase_dict['original']}\"*\n\n"
          f"👉 **Traducción:** *\"{frase_dict['traducido']}\"*"
      )
      st.write("---")


# Lógica principal
if modo == "Texto directo":
  st.subheader("Ingresa el texto de tu ensayo, puede ser en español o directamente en inglés")
  texto = st.text_area(
      "",
      height=200,
      placeholder="Escribe o pega aquí tu borrador para analizarlo...",
  )

  if st.button("🔍 Auditar Ensayo", type="primary"):
    if texto.strip():
      with st.spinner("Evaluando métricas..."):
        resultados = procesar_texto(texto)
        crear_visualizaciones(resultados)
    else:
      st.warning("Por favor, ingresa un texto para analizar.")

elif modo == "Archivo de texto":
  st.subheader("Carga tu archivo (.txt, .md)")
  archivo = st.file_uploader("", type=["txt", "csv", "md"])

  if archivo is not None:
    try:
      contenido = archivo.getvalue().decode("utf-8")
      if st.button("🔍 Auditar Archivo", type="primary"):
        with st.spinner("Procesando..."):
          resultados = procesar_texto(contenido)
          crear_visualizaciones(resultados)
    except Exception as e:
      st.error(f"Error al procesar el archivo: {e}")
