import sys
import os

# Forzar la ruta raíz del proyecto para las importaciones relacionales
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import obtener_conexion

def generar_reportes_analiticos():
    print("[+] Conectando a PostgreSQL para la extracción de métricas...")
    conexion = obtener_conexion()
    if not conexion:
        print("[-] No se pudo extraer la data para el dashboard.")
        return

    datos_crudos = []
    try:
        query = """
            SELECT p.nombre_modelo, p.marca, r.polaridad_score, r.etiqueta_sentimiento 
            FROM resenas r
            JOIN productos p ON r.id_producto = p.id_producto;
        """
        with conexion.cursor() as cursor:
            cursor.execute(query)
            datos_crudos = cursor.fetchall()
    except Exception as e:
        print(f"[-] Error durante la lectura SQL: {e}")
    finally:
        conexion.close()

    if not datos_crudos:
        print("[-] No hay datos disponibles para procesar visualizaciones.")
        return

    print(f"[+] Datos nativos importados con éxito ({len(datos_crudos)} registros analizados).")

    try:
        # 1. PROCESAMIENTO ALGORÍTMICO NATIVO
        modelos = {}
        for fila in datos_crudos:
            modelo = fila[0]
            marca = fila[1]
            polaridad = float(fila[2])
            sentimiento = fila[3]
            
            if modelo not in modelos:
                modelos[modelo] = {
                    "marca": marca,
                    "Positivo": 0, "Neutro": 0, "Negativo": 0,
                    "suma_polaridad": 0.0, "total_resenas": 0
                }
            
            if sentimiento in modelos[modelo]:
                modelos[modelo][sentimiento] += 1
            
            modelos[modelo]["suma_polaridad"] += polaridad
            modelos[modelo]["total_resenas"] += 1

        # 2. PREPARACIÓN DE FILAS PARA JAVASCRIPT Y TABLA HTML
        js_rows_barras = ""
        js_rows_lineas = ""
        tabla_html_rows = ""
        
        for mod, metricas in modelos.items():
            promedio_pol = metricas["suma_polaridad"] / metricas["total_resenas"]
            
            # Formatear filas de datos para Google Charts
            js_rows_barras += f"['{mod}', {metricas['Positivo']}, {metricas['Neutro']}, {metricas['Negativo']}],\n"
            js_rows_lineas += f"['{mod}', {promedio_pol}],\n"
            
            # Formatear filas para la tabla de datos del reporte
            tabla_html_rows += f"""
            <tr>
                <td><strong>{mod}</strong></td>
                <td>{metricas['marca']}</td>
                <td class="text-success">{metricas['Positivo']}</td>
                <td class="text-muted">{metricas['Neutro']}</td>
                <td class="text-danger">{metricas['Negativo']}</td>
                <td>{metricas['total_resenas']}</td>
                <td><span class="badge">{"%+0.2f" % promedio_pol}</span></td>
            </tr>
            """

        # 3. PLANTILLA HTML5 / CSS3 / GOOGLE CHARTS COMPLETA
        html_contenido = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Analítico NLP - MercadoLibre</title>
    
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
        google.charts.load('current', {{'packages':['corechart', 'bar']}});
        google.charts.setOnLoadCallback(drawCharts);

        function drawCharts() {{
            // Gráfico 1: Barras de Sentimiento
            var dataBarras = google.visualization.arrayToDataTable([
                ['Modelo', 'Positivo', 'Neutro', 'Negativo'],
                {js_rows_barras}
            ]);

            var optionsBarras = {{
                chartArea: {{width: '70%', height: '80%'}},
                colors: ['#2ecc71', '#f1c40f', '#e74c3c'],
                hAxis: {{ title: 'Cantidad de Reseñas', titleTextStyle: {{color: '#7f8c8d', fontSize: 11}} }},
                vAxis: {{ textStyle: {{fontSize: 11, bold: true}} }},
                bars: 'horizontal',
                legend: {{ position: 'top' }}
            }};

            var chartBarras = new google.visualization.BarChart(document.getElementById('chart_barras'));
            chartBarras.draw(dataBarras, optionsBarras);

            // Gráfico 2: Combo Chart de Polaridad Promedio
            var dataLineas = google.visualization.arrayToDataTable([
                ['Modelo', 'Polaridad Promedio'],
                {js_rows_lineas}
            ]);

            var optionsLineas = {{
                chartArea: {{width: '75%', height: '75%'}},
                colors: ['#3498db'],
                vAxis: {{ 
                    minValue: -1, 
                    maxValue: 1, 
                    title: 'Rango de Sentimiento (-1.0 a +1.0)',
                    titleTextStyle: {{color: '#7f8c8d', fontSize: 11}}
                }},
                hAxis: {{ textStyle: {{fontSize: 11, bold: true}} }},
                seriesType: 'bars',
                legend: {{ position: 'none' }}
            }};

            var chartLineas = new google.visualization.ComboChart(document.getElementById('chart_lineas'));
            chartLineas.draw(dataLineas, optionsLineas);
        }}
    </script>
    
    <style>
        :root {{
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-main: #2c3e50;
            --text-muted: #7f8c8d;
            --border-color: #e2e8f0;
            --primary: #34495e;
        }}
        
        body {{ 
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; 
            margin: 0; 
            padding: 0; 
            background-color: var(--bg-color); 
            color: var(--text-main);
        }}
        
        .header {{
            background-color: var(--primary);
            color: #ffffff;
            padding: 20px 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{ margin: 0; font-size: 1.8rem; font-weight: 600; }}
        .header p {{ margin: 5px 0 0 0; color: #bdc3c7; font-size: 0.9rem; }}
        
        .wrapper {{
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
            display: flex;
            flex-direction: column;
            gap: 30px;
        }}
        
        .grid-charts {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
        }}
        
        .card {{
            background-color: var(--card-bg);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(160, 175, 192, 0.15);
            border: 1px solid var(--border-color);
        }}
        
        .card-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 20px;
            color: var(--primary);
            border-bottom: 2px solid var(--bg-color);
            padding-bottom: 10px;
        }}
        
        .chart {{ width: 100%; height: 350px; }}
        
        /* Estilos de la Tabla */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            font-size: 0.95rem;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        th {{
            background-color: var(--bg-color);
            color: var(--primary);
            font-weight: 600;
        }}
        
        tr:hover {{ background-color: #f8fafc; }}
        
        .text-success {{ color: #2ecc71; font-weight: bold; }}
        .text-muted {{ color: #95a5a6; font-weight: bold; }}
        .text-danger {{ color: #e74c3c; font-weight: bold; }}
        
        .badge {{
            background-color: var(--primary);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            margin: 4px 0 30px 0;
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>

    <div class="header">
        <h1>📊 Sistema Monolítico NLP - Dashboard Analítico</h1>
        <p>Pipeline de Procesamiento por Lotes y Análisis de Sentimientos en Smartphones (MercadoLibre)</p>
    </div>

    <div class="wrapper">
        <div class="grid-charts">
            <div class="card">
                <div class="card-title">Métrica 1: Distribución Categórica de Sentimientos</div>
                <div id="chart_barras" class="chart"></div>
            </div>
            <div class="card">
                <div class="card-title">Métrica 2: Score de Polaridad Promedio (-1.0 a +1.0)</div>
                <div id="chart_lineas" class="chart"></div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">Resumen de Métricas Consolidadas (Data Warehouse Local)</div>
            <table>
                <thead>
                    <tr>
                        <th>Modelo del Equipo</th>
                        <th>Marca</th>
                        <th>Positivos</th>
                        <th>Neutros</th>
                        <th>Negativos</th>
                        <th>Total Reseñas</th>
                        <th>Polaridad Promedio</th>
                    </tr>
                </thead>
                <tbody>
                    {tabla_html_rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Universidad Tecnológica Israel • Proyecto de Fin de Semestre • Ingeniería en TI
        </div>
    </div>

</body>
</html>
"""

        # 4. VOLCADO DIRECTO EN DISCO
        reporte_path = "dashboard_analitico.html"
        with open(reporte_path, "w", encoding="utf-8") as f:
            f.write(html_contenido)
            
        print(f"\n[+] ¡Dashboard actualizado con éxito absoluto!")
        print(f"[+] Archivo guardado como: {reporte_path}")
        print("[+] Haz doble clic sobre 'dashboard_analitico.html' para abrir la nueva interfaz interactiva.")

    except Exception as e:
        print(f"[-] Error en el procesamiento estructural: {e}")

if __name__ == "__main__":
    generar_reportes_analiticos()