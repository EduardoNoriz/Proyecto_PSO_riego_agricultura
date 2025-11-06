"""
Script principal del proyecto PSO para optimización de riego agrícola
Coordina la ejecución de todos los módulos y presenta resultados
"""

import numpy as np
import pandas as pd
from configuraciones import configuracion_aleatoria, configuracion_centros_cultivo, configuracion_zonas_criticas
from algoritmo_pso import PSOOptimizer
from visualizaciones import (visualizar_comparacion_configuraciones, visualizar_cobertura_detallada,
                           visualizar_analisis_eficiencia)

def crear_datos_ejemplo():
    """
    Generar datos de ejemplo para pruebas del sistema
    
    Returns:
        DataFrame: Datos simulados de cultivos con coordenadas geográficas
    """
    np.random.seed(42)
    
    datos = {
        'Humedad': np.random.uniform(5, 45, 100),
        'Cultivo': np.random.choice(['Maíz', 'Tomate', 'Chile'], 100, p=[0.5, 0.3, 0.2]),
        'Elevacion': np.random.uniform(10, 50, 100),
        'Salinidad': np.random.uniform(0.5, 4.0, 100),
        'Temperatura': np.random.uniform(20, 40, 100),
        'Latitud': np.random.uniform(25.52, 25.62, 100),
        'Longitud': np.random.uniform(-108.52, -108.42, 100)
    }
    
    return pd.DataFrame(datos)

def comparar_configuraciones_manuales(datos, n_sensores=5):
    """
    Comparar diferentes estrategias manuales de ubicación de sensores
    
    Args:
        datos: DataFrame con datos de cultivos
        n_sensores: Número de sensores a ubicar
    
    Returns:
        dict: Configuraciones y sus puntajes
    """
    print("Comparando configuraciones manuales...")
    
    configuraciones = {
        'Aleatoria': configuracion_aleatoria(n_sensores, datos),
        'Centros Cultivo': configuracion_centros_cultivo(n_sensores, datos),
        'Zonas Criticas': configuracion_zonas_criticas(n_sensores, datos)
    }
    
    # Mostrar puntajes de configuraciones manuales
    print("Puntajes de configuraciones manuales:")
    for nombre, sensores in configuraciones.items():
        from funciones_objetivo import funcion_objetivo
        puntaje = funcion_objetivo(sensores, datos)
        print(f"  {nombre}: {puntaje:.4f}")
    
    return configuraciones

def ejecutar_optimizacion_pso(datos, n_sensores=5, n_particulas=25, max_iter=80):
    """
    Ejecutar optimización con algoritmo PSO
    
    Args:
        datos: DataFrame con datos de cultivos
        n_sensores: Número de sensores a optimizar
        n_particulas: Tamaño del enjambre
        max_iter: Número máximo de iteraciones
    
    Returns:
        tuple: (sensores_optimos, puntaje_optimo)
    """
    print("\nEjecutando optimizacion PSO...")
    
    pso = PSOOptimizer(datos, n_sensores=n_sensores, n_particulas=n_particulas, max_iter=max_iter)
    sensores_optimos, puntaje_optimo = pso.optimizar()
    
    # Mostrar curva de convergencia
    pso.visualizar_convergencia()
    
    return sensores_optimos, puntaje_optimo

def mostrar_resultados_finales(configuraciones, sensores_pso, puntaje_pso, datos):
    """
    Presentar resultados finales y comparaciones
    
    Args:
        configuraciones: Diccionario con configuraciones manuales
        sensores_pso: Sensores optimizados por PSO
        puntaje_pso: Puntaje de la configuración PSO
        datos: DataFrame con datos de cultivos
    """
    # Agregar configuración PSO al diccionario
    configuraciones['PSO Optimo'] = sensores_pso
    
    # Mostrar comparación visual
    visualizar_comparacion_configuraciones(configuraciones, datos)
    
    # Análisis detallado de la solución PSO
    visualizar_cobertura_detallada(sensores_pso, datos, "Solucion PSO Optima")
    visualizar_analisis_eficiencia(sensores_pso, datos)
    
    # Resumen numérico final
    print("\n" + "="*60)
    print("RESUMEN FINAL DE PUNTAJES")
    print("="*60)
    
    from funciones_objetivo import funcion_objetivo
    for nombre, sensores in configuraciones.items():
        puntaje = funcion_objetivo(sensores, datos)
        print(f"{nombre:<20}: {puntaje:.4f}")
    
    # Calcular mejora del PSO
    mejor_manual = max([funcion_objetivo(sensores, datos) 
                       for nombre, sensores in configuraciones.items() if nombre != 'PSO Optimo'])
    mejora = ((puntaje_pso - mejor_manual) / mejor_manual) * 100
    
    print(f"\nMejora del PSO sobre mejor metodo manual: {mejora:+.1f}%")
    
    # Mostrar ubicaciones óptimas
    print(f"\nUbicaciones optimas de sensores PSO:")
    for i, sensor in enumerate(sensores_pso):
        print(f"  Sensor {i+1}: Lat = {sensor[0]:.6f}, Lon = {sensor[1]:.6f}")

def main():
    """
    Función principal que coordina la ejecución completa del proyecto
    """
    print("="*70)
    print("      PROYECTO PSO - OPTIMIZACION DE SENSORES DE RIEGO")
    print("="*70)
    
    # Paso 1: Cargar o generar datos
    print("\n1. CARGANDO DATOS...")
    datos = crear_datos_ejemplo()
    print(f"   Datos cargados: {len(datos)} puntos de muestreo")
    print(f"   Distribucion de cultivos:")
    print(f"   {datos['Cultivo'].value_counts().to_string()}")
    
    # Paso 2: Comparar métodos manuales
    print("\n2. COMPARANDO ESTRATEGIAS MANUALES...")
    configuraciones = comparar_configuraciones_manuales(datos, n_sensores=5)
    
    # Paso 3: Optimización con PSO
    print("\n3. OPTIMIZACION CON ALGORITMO PSO...")
    sensores_pso, puntaje_pso = ejecutar_optimizacion_pso(datos, n_sensores=5, n_particulas=25, max_iter=80)
    
    # Paso 4: Resultados y análisis
    print("\n4. ANALISIS DE RESULTADOS...")
    mostrar_resultados_finales(configuraciones, sensores_pso, puntaje_pso, datos)
    
    print("\n" + "="*70)
    print("                    EJECUCION COMPLETADA")
    print("="*70)

if __name__ == "__main__":
    main()