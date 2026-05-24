import os
import psycopg  # Usamos exclusivamente la versión 3 que instaló con éxito

def obtener_conexion():
    """
    Establece la conexión con el servidor de PostgreSQL de forma segura usando psycopg v3.
    """
    try:
        # Adaptado a tus credenciales locales reales
        conexion = psycopg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            dbname=os.getenv("DB_NAME", "mercado_analitica"), # 'dbname' en v3
            user=os.getenv("DB_USER", "postgres"),       # Tu usuario
            password=os.getenv("DB_PASSWORD", "1992"),        # Tu contraseña
            port=os.getenv("DB_PORT", "5432")
        )
        return conexion
    except psycopg.DatabaseError as e:
        print(f"[-] Error crítico al conectar a PostgreSQL: {e}")
        return None

def inicializar_base_de_datos(ruta_sql="database/schema.sql"):
    """
    Lee el archivo DDL (schema.sql) y crea la estructura de tablas 
    en la base de datos si aún no existen.
    """
    conexion = obtener_conexion()
    if not conexion:
        return

    try:
        with conexion.cursor() as cursor:
            # Verificar si existe el archivo de esquema
            if os.path.exists(ruta_sql):
                with open(ruta_sql, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                
                # Ejecutar el script DDL
                cursor.execute(sql_script)
                conexion.commit()  # Confirmar la creación de tablas
                print("[+] Infraestructura relacional inicializada correctamente (Tablas verificadas/creadas).")
            else:
                print(f"[-] No se encontró el archivo de esquema SQL en la ruta: {ruta_sql}")
    except psycopg.DatabaseError as e:
        print(f"[-] Error durante la inicialización de las tablas: {e}")
        conexion.rollback()
    finally:
        conexion.close()

def insertar_producto(nombre_modelo, marca):
    """
    Inserta un nuevo smartphone en la tabla 'productos' y retorna su ID.
    Si ya existe debido a la restricción UNIQUE, recupera el ID existente.
    """
    query_insert = """
        INSERT INTO productos (nombre_modelo, marca) 
        VALUES (%s, %s) 
        ON CONFLICT (nombre_modelo) DO UPDATE SET nombre_modelo = EXCLUDED.nombre_modelo
        RETURNING id_producto;
    """
    conexion = obtener_conexion()
    id_producto = None

    if not conexion:
        return None

    try:
        with conexion.cursor() as cursor:
            cursor.execute(query_insert, (nombre_modelo, marca))
            id_producto = cursor.fetchone()[0]
            conexion.commit()
    except psycopg.DatabaseError as e:
        print(f"[-] Error al insertar producto ({nombre_modelo}): {e}")
        conexion.rollback()
    finally:
        conexion.close()
        
    return id_producto

# Bloque de prueba de conectividad local
if __name__ == "__main__":
    print("[+] Probando la conexión e inicializando la base de datos con Psycopg v3...")
    inicializar_base_de_datos()