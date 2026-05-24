import sys
from config.database import inicializar_base_de_datos, obtener_conexion
from src.scraper import extraer_html_pagina, parsear_opiniones
from src.nlp_pipeline import limpiar_texto, evaluar_sentimiento

def ejecutar_pipeline_batch():
    print("[+] Iniciando el sistema de procesamiento por lotes...")
    
    # 1. Asegurar que la infraestructura relacional exista
    inicializar_base_de_datos()
    
    # 2. Definición del catálogo de smartphones a analizar con URLs reales
    smartphones_objetivo = [
        {
            "modelo": "Xiaomi Redmi Note 13",
            "marca": "Xiaomi",
            "url": "https://www.mercadolibre.com.ec/xiaomi-redmi-note-13-pro-plus-5g-nfc-dual-512-gb-negro-12-gb/p/MEC43277495#reviews" 
        },
        {
            "modelo": "Samsung Galaxy A56",
            "marca": "Samsung",
            "url": "https://www.mercadolibre.com.ec/samsung-galaxy-a56-5g-dual-sim-256gb-12gb-negro-67/p/MEC47797906#reviews"
        }
    ]
    
    # Abrir conexión global única para todo el lote
    conexion = obtener_conexion()
    if not conexion:
        print("[-] No se pudo establecer la conexión para la carga masiva. Abortando.")
        sys.exit(1)
        
    try:
        with conexion.cursor() as cursor:
            for equipo in smartphones_objetivo:
                print(f"\n[+] Procesando producto: {equipo['modelo']}")
                
                # OPTIMIZACIÓN: Insertar el producto usando el MISMO cursor global para evitar bloqueos
                query_insert_producto = """
                    INSERT INTO productos (nombre_modelo, marca) 
                    VALUES (%s, %s) 
                    ON CONFLICT (nombre_modelo) DO UPDATE SET nombre_modelo = EXCLUDED.nombre_modelo
                    RETURNING id_producto;
                """
                cursor.execute(query_insert_producto, (equipo["modelo"], equipo["marca"]))
                id_producto = cursor.fetchone()[0]
                
                # Extraer HTML de la plataforma web externa
                html_crudo = extraer_html_pagina(equipo["url"])
                if not html_crudo:
                    print(f"[-] Saltando {equipo['modelo']} debido a fallos de red.")
                    continue
                
                # Parsear los bloques de opiniones desde el DOM
                opiniones = parsear_opiniones(html_crudo)
                print(f"[+] Se localizaron {len(opiniones)} reseñas para procesar.")
                
                # Recorrer las reseñas obtenidas para aplicar NLP y persistencia
                for op in opiniones:
                    texto_crudo = op["texto_resena"]
                    estrellas = op["calificacion_numerica"]
                    
                    # Pasar la reseña por el Subsistema de Analítica de Texto (NLP)
                    texto_limpio = limpiar_texto(texto_crudo)
                    polaridad_score, etiqueta = evaluar_sentimiento(texto_limpio)
                    
                    # Sentencia estructurada INSERT para gestionar la persistencia segura
                    query_insert_resena = """
                        INSERT INTO resenas (id_producto, calificacion_numerica, texto_resena, texto_limpio, polaridad_score, etiqueta_sentimiento)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """
                    
                    cursor.execute(query_insert_resena, (
                        id_producto,
                        estrellas,
                        texto_crudo,
                        texto_limpio,
                        polaridad_score,
                        etiqueta
                    ))
                
                # Aplicar transacciones seguras por lote de producto (COMMIT)
                conexion.commit()
                print(f"[+] Lote de {equipo['modelo']} almacenado de forma exitosa.")
                
    except Exception as e:
        print(f"[-] Error crítico durante la ejecución del lote: {e}")
        conexion.rollback()  # Garantiza la atomicidad de los datos si algo falla
    finally:
        conexion.close()
        print("\n[+] Ejecución del pipeline finalizada.")

if __name__ == "__main__":
    ejecutar_pipeline_batch()