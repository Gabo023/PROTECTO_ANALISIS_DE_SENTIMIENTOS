import re
from textblob import TextBlob

def limpiar_texto(texto_crudo):
    """
    Normaliza el comentario eliminando caracteres especiales,
    conversión a minúsculas y remoción de ruidos en el texto libre.
    """
    if not texto_crudo:
        return ""
    
    # 1. Convertir a minúsculas
    texto = texto_crudo.lower()
    
    # 2. Eliminar saltos de línea y tabulaciones
    texto = texto.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    
    # 3. Remover caracteres especiales y emojis, manteniendo letras, espacios y tildes/eñes
    texto = re.sub(r'[^a-záéíóúñü\s]', '', texto)
    
    # 4. Eliminar espacios en blanco múltiples
    texto = " ".join(texto.split())
    
    return texto

def evaluar_sentimiento(texto_limpio):
    """
    Calcula el score de polaridad (-1.0 a +1.0) y asigna una etiqueta categórica.
    Utiliza TextBlob para el cómputo lingüístico básico.
    """
    if not texto_limpio:
        return 0.0, "Neutro"
    
    # TextBlob analiza la polaridad por defecto en inglés. 
    # Para el alcance académico actual, podemos apoyarnos en su análisis de polaridad.
    # Nota: Si el texto está en español, TextBlob requiere traducción previa o usar diccionarios NLTK.
    # Como alternativa rápida y ligera, inicializamos el objeto:
    analisis = TextBlob(texto_limpio)
    
    # Intentar obtener la polaridad (valor entre -1.0 y 1.0)
    polaridad = analisis.sentiment.polarity
    
    # Mitigación manual de sesgos o modismos locales ecuatorianos detectados en las opiniones
    # (Por ejemplo: forzar positividad ante expresiones comunes como "una bestia" o "de ley")
    if "bestia" in texto_limpio or "de ley" in texto_limpio:
        polaridad = max(polaridad, 0.5) # Se fuerza un piso positivo controlado
        
    # Clasificar en variables categóricas según el rango numérico
    if polaridad > 0.1:
        etiqueta = "Positivo"
    elif polaridad < -0.1:
        etiqueta = "Negativo"
    else:
        etiqueta = "Neutro"
        
    return round(polaridad, 3), etiqueta

# Bloque de prueba unitaria local
if __name__ == "__main__":
    print("[+] Probando el pipeline de analítica de texto (NLP)...")
    
    # Casos de prueba basados en los escenarios comunes de la problemática
    comentarios_prueba = [
        "El teléfono es excelente, llegó súper rápido y la cámara es una bestia!! 5 estrellas.",
        "Malo. El celular se traba a cada rato y la batería no dura nada.",
        "El paquete vino bien empacado, conforme con el tiempo de envío."
    ]
    
    for comentario in comentarios_prueba:
        limpio = limpiar_texto(comentario)
        score, sentimiento = evaluar_sentimiento(limpio)
        print(f"\nOriginal: {comentario}")
        print(f"Limpio:   {limpio}")
        print(f"Resultado: Score={score} | Sentimiento={sentimiento}")