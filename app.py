import re
from googletrans import Translator
import pandas as pd
import streamlit as st
from textblob import TextBlob

# Configuración de la página
st.set_page_config(
    page_title="Essay Tone & Sentiment Auditor", page_icon="🎓", layout="wide"
)

# Título y descripción orientados a la educación/escritura
st.title("🎓 Auditor de Ensayos en Inglés")
st.markdown("""
Evalúa el **tono**, la **objetividad** y la **polaridad** de tu ensayo académico antes de entregarlo.
El sistema traduce las ideas, analiza la carga emocional y valida si el texto cumple con el estándar de objetividad deseado.
""")

# Barra lateral
st.sidebar.title("📌 Configuración de Ensayo")
modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:", ["Texto directo", "Archivo de texto"]
)

st.sidebar.info("""
**Criterios de Evaluación:**
- **Subjetividad < 0.40:** Ideal para Ensayos Argumentativos y Científicos.
- **Subjetividad > 0.50:** Recomendado para Ensayos Narrativos o Reflexiones Personales.
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

  contador_ordenado = dict(
      sorted(contador.items(), key=lambda x: x[1], reverse=True)
  )
  return contador_ordenado, palabras_filtradas


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

    # Métrica de Objetividad
    st.write("**Nivel de Subjetividad / Juicio Personal:**")
    st.progress(resultados["subjetividad"])

    if resultados["subjetividad"] < 0.35:
      st.success(
          f"🎯 **Estilo Objetivo Académico** ({resultados['subjetividad']:.2f})"
          " - Excelente para ensayos argumentativos."
      )
    elif resultados["subjetividad"] <= 0.60:
      st.warning(
          f"⚖️ **Tono Mixto** ({resultados['subjetividad']:.2f}) - Contiene"
          " opiniones personales combinadas con datos."
      )
    else:
      st.error(
          f"💭 **Alta Subjetividad** ({resultados['subjetividad']:.2f}) - Cuidado:"
          " Puede sonar más a opinión personal que a ensayo formal."
      )

    # Métrica de Polaridad
    sentimiento_norm = (resultados["sentimiento"] + 1) / 2
    st.write("**Polaridad Emocional del Argumento:**")
    st.progress(sentimiento_norm)

    if resultados["sentimiento"] > 0.1:
      st.info(
          f"📈 **Enfoque Positivo/Propositivo** ({resultados['sentimiento']:.2f})"
      )
    elif resultados["sentimiento"] < -0.1:
      st.info(
          f"📉 **Enfoque Crítico/Negativo** ({resultados['sentimiento']:.2f})"
      )
    else:
      st.success(
          f"⚖️ **Tono Totalmente Neutro** ({resultados['sentimiento']:.2f})"
      )

  with col2:
    st.subheader("🔑 Vocabulario Académico Clave")
    if resultados["contador_palabras"]:
      palabras_top = dict(list(resultados["contador_palabras"].items())[:8])
      st.bar_chart(palabras_top)
      st.caption("Palabras relevantes detectadas en la versión en inglés.")

  st.divider()

  # Revisión frase a frase
  st.subheader("🔍 Desglose de Argumentos por Frase")
  if resultados["frases"]:
    for i, frase_dict in enumerate(resultados["frases"][:8], 1):
      frase_original = frase_dict["original"]
      frase_traducida = frase_dict["traducido"]

      blob_frase = TextBlob(frase_traducida)
      sent = blob_frase.sentiment.polarity
      subj = blob_frase.sentiment.subjectivity

      st.markdown(
          f"**{i}. Original:** *\"{frase_original}\"*\n\n"
          f"👉 **Traducción al Inglés:** *\"{frase_traducida}\"*\n\n"
          f"📌 *Polaridad:* `{sent:.2f}` | *Subjetividad:* `{subj:.2f}`"
      )
      st.write("---")


# Lógica principal
if modo == "Texto directo":
  st.subheader("Ingresa el borrador de tu ensayo")
  texto = st.text_area(
      "",
      height=200,
      placeholder=(
          "Pega aquí tu ensayo en español o inglés para analizar el tono..."
      ),
  )

  if st.button("🔍 Auditar Ensayo", type="primary"):
    if texto.strip():
      with st.spinner("Evaluando métricas académicas..."):
        resultados = procesar_texto(texto)
        crear_visualizaciones(resultados)
    else:
      st.warning("Por favor, ingresa el texto del ensayo a analizar.")

elif modo == "Archivo de texto":
  st.subheader("Carga tu ensayo (.txt, .md)")
  archivo = st.file_uploader("", type=["txt", "csv", "md"])

  if archivo is not None:
    try:
      contenido = archivo.getvalue().decode("utf-8")
      if st.button("🔍 Auditar Archivo", type="primary"):
        with st.spinner("Procesando archivo..."):
          resultados = procesar_texto(contenido)
          crear_visualizaciones(resultados)
    except Exception as e:
      st.error(f"Error al procesar el archivo: {e}")
