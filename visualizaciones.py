"""
Módulo de visualización para el proyecto PSO de optimización de riego
Genera gráficos y mapas para analizar resultados y configuraciones
"""

import numpy as np
import matplotlib.pyplot as plt
from math import pi  # Corregido: sin guión bajo
from scipy.spatial import Delaunay  # Corregido: sin guión bajo
from config import CONFIG
from funciones_objetivo import (  # Corregido: "objetivo" no "objectivo"
    calcular_cobertura_variabilidad, 
    balance_entre_cultivos,
    cubrir_zonas_problematicas, 
    optimizar_distancias, 
    funcion_objetivo  # Corregido: "objetivo" no "objectivo"
)

def visualizar_comparacion_configuraciones(configuraciones, datos):
    """
    Comparar visualmente diferentes configuraciones de sensores
    
    Args:
        configuraciones: Diccionario {nombre: lista_de_sensores}
        datos: DataFrame con puntos de muestreo
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    axes = axes.flatten()
    
    for idx, (nombre, sensores) in enumerate(configuraciones.items()):
        if idx >= len(axes):
            break
            
        ax = axes[idx]
        puntaje = funcion_objetivo(sensores, datos)
        
        # Colores por cultivo
        for cultivo, color in zip(['Maíz', 'Tomate', 'Chile'], ['green', 'red', 'orange']):
            puntos_cultivo = datos[datos['Cultivo'] == cultivo]
            ax.scatter(puntos_cultivo['Longitud'], puntos_cultivo['Latitud'], 
                      c=color, label=cultivo, alpha=0.5, s=30)
        
        # Sensores
        sensores_array = np.array(sensores)
        ax.scatter(sensores_array[:, 1], sensores_array[:, 0], 
                  c='blue', marker='X', s=150, label='Sensores', edgecolors='black')
        
        # Zonas críticas
        zonas_criticas = datos[(datos['Salinidad'] > 2.5) | (datos['Humedad'] < 15) | (datos['Humedad'] > 40)]
        ax.scatter(zonas_criticas['Longitud'], zonas_criticas['Latitud'],
                  c='black', marker='s', s=50, label='Zonas Criticas', alpha=0.8)
        
        ax.set_xlabel('Longitud')
        ax.set_ylabel('Latitud')
        ax.set_title(f'{nombre}\nPuntaje: {puntaje:.3f}')
        ax.grid(True, alpha=0.3)
        
        if idx == 0:  # Solo mostrar leyenda en el primer gráfico
            ax.legend()
    
    # Ocultar ejes vacíos si los hay
    for idx in range(len(configuraciones), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.show()

def visualizar_radar_componentes(puntajes, titulo="Analisis de Componentes"):
    """
    Crear gráfico radar para visualizar balance entre componentes de la función objetivo
    
    Args:
        puntajes: Diccionario con puntajes de cada componente
        titulo: Título del gráfico
    """
    componentes = ['Cobertura', 'Balance\nCultivos', 'Zonas\nCriticas', 'Distribucion']
    valores = list(puntajes.values())
    
    # Cerrar el gráfico repitiendo el primer valor
    valores += valores[:1]
    angulos = [n / float(len(componentes)) * 2 * pi for n in range(len(componentes))]
    angulos += angulos[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    ax.plot(angulos, valores, 'o-', linewidth=2, label='Puntajes')
    ax.fill(angulos, valores, alpha=0.25)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(componentes)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.grid(True)
    plt.title(titulo, size=14, y=1.08)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    plt.show()

def visualizar_cobertura_detallada(sensores, datos, titulo="Mapa de Cobertura Detallada"):
    """
    Visualizar configuración de sensores con áreas de cobertura e influencia
    
    Args:
        sensores: Lista de sensores [[lat, lon], ...]
        datos: DataFrame con puntos de muestreo
        titulo: Título del gráfico
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Colores distintos para cada sensor
    colores_sensores = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    # Plotear puntos de datos por cultivo
    for cultivo, color in zip(['Maíz', 'Tomate', 'Chile'], ['green', 'red', 'orange']):
        puntos_cultivo = datos[datos['Cultivo'] == cultivo]
        ax1.scatter(puntos_cultivo['Longitud'], puntos_cultivo['Latitud'], 
                   c=color, label=cultivo, alpha=0.6, s=40)
        ax2.scatter(puntos_cultivo['Longitud'], puntos_cultivo['Latitud'], 
                   c=color, label=cultivo, alpha=0.6, s=40)
    
    # Plotear sensores y áreas de cobertura
    for i, sensor in enumerate(sensores):
        color_sensor = colores_sensores[i % len(colores_sensores)]
        
        # Marcador de sensor
        ax1.scatter(sensor[1], sensor[0], c=color_sensor, marker='X', s=200, 
                   label=f'Sensor {i+1}', edgecolors='black', linewidth=2)
        ax2.scatter(sensor[1], sensor[0], c=color_sensor, marker='X', s=200, 
                   label=f'Sensor {i+1}', edgecolors='black', linewidth=2)
        
        # Círculo de cobertura básica
        circulo_cobertura = plt.Circle((sensor[1], sensor[0]), CONFIG['radio_cobertura'], 
                           color=color_sensor, alpha=0.2)
        ax1.add_patch(circulo_cobertura)
        
        # Círculo de área de influencia
        circulo_influencia = plt.Circle((sensor[1], sensor[0]), CONFIG['radio_influencia'], 
                                      color=color_sensor, alpha=0.1)
        ax2.add_patch(circulo_influencia)
    
    # Marcar zonas críticas
    zonas_criticas = datos[(datos['Salinidad'] > 2.5) | (datos['Humedad'] < 15) | (datos['Humedad'] > 40)]
    ax1.scatter(zonas_criticas['Longitud'], zonas_criticas['Latitud'],
               c='black', marker='s', s=60, label='Zonas Criticas', alpha=0.8)
    ax2.scatter(zonas_criticas['Longitud'], zonas_criticas['Latitud'],
               c='black', marker='s', s=60, label='Zonas Criticas', alpha=0.8)
    
    ax1.set_xlabel('Longitud')
    ax1.set_ylabel('Latitud')
    ax1.set_title(f'{titulo} - Areas de Cobertura')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Longitud')
    ax2.set_ylabel('Latitud')
    ax2.set_title(f'{titulo} - Areas de Influencia')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def visualizar_analisis_eficiencia(sensores, datos):
    """
    Generar análisis completo de eficiencia con múltiples visualizaciones
    
    Args:
        sensores: Lista de sensores [[lat, lon], ...]
        datos: DataFrame con puntos de muestreo
    """
    # Calcular métricas detalladas
    cobertura_total = calcular_cobertura_variabilidad(sensores, datos)
    balance = balance_entre_cultivos(sensores, datos)
    zonas_criticas = cubrir_zonas_problematicas(sensores, datos)
    distribucion = optimizar_distancias(sensores)
    
    # Calcular cobertura por tipo de cultivo
    cobertura_por_cultivo = {}
    radio = CONFIG['radio_cobertura']
    
    for cultivo in ['Maíz', 'Tomate', 'Chile']:
        puntos_cultivo = datos[datos['Cultivo'] == cultivo]
        cubiertos = 0
        
        for _, punto in puntos_cultivo.iterrows():
            punto_coords = [punto['Latitud'], punto['Longitud']]
            if any(np.sqrt((punto_coords[0]-s[0])**2 + (punto_coords[1]-s[1])**2) <= radio for s in sensores):
                cubiertos += 1
        
        cobertura_por_cultivo[cultivo] = cubiertos / len(puntos_cultivo)
    
    # Crear figura con 4 subgráficos
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Subgráfico 1: Componentes principales
    componentes = ['Cobertura', 'Balance', 'Zonas Criticas', 'Distribucion']
    valores = [cobertura_total, balance, zonas_criticas, distribucion]
    colores = ['skyblue', 'lightgreen', 'lightcoral', 'gold']
    
    bars = ax1.bar(componentes, valores, color=colores, alpha=0.8)
    ax1.set_ylabel('Puntaje')
    ax1.set_title('Analisis de Componentes Principales')
    ax1.set_ylim(0, 1)
    
    # Añadir valores en las barras
    for bar, valor in zip(bars, valores):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{valor:.3f}', ha='center', va='bottom')
    
    # Subgráfico 2: Cobertura por cultivo
    cultivos = list(cobertura_por_cultivo.keys())
    coberturas = list(cobertura_por_cultivo.values())
    
    bars2 = ax2.bar(cultivos, coberturas, color=['green', 'red', 'orange'], alpha=0.8)
    ax2.set_ylabel('Porcentaje Cubierto')
    ax2.set_title('Cobertura por Tipo de Cultivo')
    ax2.set_ylim(0, 1)
    
    for bar, valor in zip(bars2, coberturas):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{valor:.1%}', ha='center', va='bottom')
    
    # Subgráfico 3: Distribución espacial
    sensores_array = np.array(sensores)
    ax3.scatter(sensores_array[:, 1], sensores_array[:, 0], s=100, c='blue', alpha=0.7)
    
    # Triangulación para mostrar distribución
    if len(sensores) >= 3:
        try:
            tri = Delaunay(sensores_array)
            ax3.triplot(sensores_array[:, 1], sensores_array[:, 0], tri.simplices, color='red', alpha=0.5)
        except:
            pass  # Continuar sin triangulación si falla
    
    ax3.set_xlabel('Longitud')
    ax3.set_ylabel('Latitud')
    ax3.set_title('Distribucion y Triangulacion de Sensores')
    ax3.grid(True, alpha=0.3)
    
    # Subgráfico 4: Resumen numérico
    ax4.axis('off')
    zonas_criticas_total = len(datos[(datos['Salinidad'] > 2.5) | (datos['Humedad'] < 15) | (datos['Humedad'] > 40)])
    distancias = [np.sqrt((sensores[i][0]-sensores[j][0])**2 + (sensores[i][1]-sensores[j][1])**2) 
                 for i in range(len(sensores)) for j in range(i+1, len(sensores))]
    
    resumen_text = (
        f"RESUMEN DE EFICIENCIA\n\n"
        f"Puntaje Total: {funcion_objetivo(sensores, datos):.3f}\n"
        f"Sensores Utilizados: {len(sensores)}\n"
        f"Puntos Cubiertos: {int(cobertura_total * len(datos))}/{len(datos)}\n"
        f"Zonas Criticas Cubiertas: {int(zonas_criticas * zonas_criticas_total)}/{zonas_criticas_total}\n"
        f"Distancia Promedio: {np.mean(distancias):.4f} grados"
    )
    ax4.text(0.1, 0.9, resumen_text, transform=ax4.transAxes, fontsize=12, 
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
    
    plt.tight_layout()
    plt.show()
    
    # Gráfico radar adicional
    puntajes_radar = {
        'cobertura': cobertura_total,
        'balance': balance,
        'criticas': zonas_criticas,
        'distribucion': distribucion
    }
    visualizar_radar_componentes(puntajes_radar, "Analisis de Eficiencia por Componente")