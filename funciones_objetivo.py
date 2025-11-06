"""
Módulo con las funciones objetivo para evaluar configuraciones de sensores
Incluye componentes de cobertura, balance de cultivos y optimización espacial
"""

import numpy as np
import pandas as pd
from config import CONFIG

def calcular_distancia(punto1, punto2):
    """
    Calcular distancia euclidiana entre dos puntos geográficos
    
    Args:
        punto1: Lista [latitud, longitud]
        punto2: Lista [latitud, longitud]
    
    Returns:
        float: Distancia en grados decimales
    """
    return np.sqrt((punto1[0] - punto2[0])**2 + (punto1[1] - punto2[1])**2)

def calcular_cobertura_variabilidad(ubicaciones_sensores, datos):
    """
    Evaluar cobertura espacial de los sensores
    
    Calcula qué porcentaje del área está cubierto por los sensores,
    considerando un radio de cobertura específico.
    
    Args:
        ubicaciones_sensores: Lista de sensores [[lat, lon], ...]
        datos: DataFrame con puntos de muestreo
    
    Returns:
        float: Puntaje de cobertura normalizado [0,1]
    """
    puntaje = 0
    total_puntos = len(datos)
    radio = CONFIG['radio_cobertura']
    
    for _, punto in datos.iterrows():
        punto_coords = [punto['Latitud'], punto['Longitud']]
        # Calcular distancia al sensor más cercano
        distancias = [calcular_distancia(punto_coords, sensor) for sensor in ubicaciones_sensores]
        dist_minima = min(distancias)
        
        # Puntaje completo si está dentro del radio, reducido si está fuera
        if dist_minima <= radio:
            puntaje += 1
        else:
            # Puntaje decreciente con la distancia
            puntaje += max(0, 1 - (dist_minima - radio) / (2 * radio))
    
    return puntaje / total_puntos

def balance_entre_cultivos(ubicaciones_sensores, datos):
    """
    Evaluar balance en la cobertura de diferentes tipos de cultivo
    
    Asegura que todos los tipos de cultivo reciban cobertura proporcional
    a su presencia en el área de estudio.
    
    Args:
        ubicaciones_sensores: Lista de sensores [[lat, lon], ...]
        datos: DataFrame con puntos de muestreo
    
    Returns:
        float: Puntaje de balance normalizado [0,1]
    """
    conteo_total = datos['Cultivo'].value_counts()
    conteo_cubierto = {'Maíz': 0, 'Tomate': 0, 'Chile': 0}
    radio = CONFIG['radio_influencia']
    
    # Contar puntos cubiertos por cultivo
    for cultivo in conteo_cubierto.keys():
        puntos_cultivo = datos[datos['Cultivo'] == cultivo]
        
        for _, punto in puntos_cultivo.iterrows():
            punto_coords = [punto['Latitud'], punto['Longitud']]
            cubierto = any(calcular_distancia(punto_coords, sensor) <= radio 
                          for sensor in ubicaciones_sensores)
            
            if cubierto:
                conteo_cubierto[cultivo] += 1
    
    # Calcular puntaje de balance
    puntaje_balance = 0
    for cultivo in conteo_cubierto:
        proporcion_ideal = conteo_total[cultivo] / len(datos)
        cobertura_real = conteo_cubierto[cultivo] / conteo_total[cultivo]
        diferencia = abs(proporcion_ideal - cobertura_real)
        puntaje_cultivo = 1 - diferencia
        puntaje_balance += min(puntaje_cultivo, 1.0)  # Limitar a máximo 1.0
    
    return puntaje_balance / len(conteo_cubierto)

def cubrir_zonas_problematicas(ubicaciones_sensores, datos):
    """
    Evaluar cobertura de zonas con problemas específicos
    
    Prioriza la cobertura de áreas con alta salinidad o humedad extrema
    que requieren monitoreo más intensivo.
    
    Args:
        ubicaciones_sensores: Lista de sensores [[lat, lon], ...]
        datos: DataFrame con puntos de muestreo
    
    Returns:
        float: Puntaje de cobertura de zonas críticas [0,1]
    """
    # Identificar zonas críticas basadas en condiciones del suelo
    zonas_criticas = datos[
        (datos['Salinidad'] > 2.5) |   # Alta salinidad
        (datos['Humedad'] < 15) |      # Muy secas
        (datos['Humedad'] > 40)        # Muy húmedas
    ]
    
    if len(zonas_criticas) == 0:
        return 1.0  # Si no hay zonas críticas, puntaje perfecto
    
    puntos_cubiertos = 0
    radio_critico = 0.01  # Radio más estricto para zonas críticas
    
    for _, punto_critico in zonas_criticas.iterrows():
        punto_coords = [punto_critico['Latitud'], punto_critico['Longitud']]
        cubierto = any(calcular_distancia(punto_coords, sensor) <= radio_critico 
                      for sensor in ubicaciones_sensores)
        if cubierto:
            puntos_cubiertos += 1
    
    return puntos_cubiertos / len(zonas_criticas)

def optimizar_distancias(ubicaciones_sensores):
    """
    Optimizar la distribución espacial de los sensores
    
    Evalúa si los sensores están bien distribuidos en el espacio,
    evitando aglomeraciones y áreas sin cobertura.
    
    Args:
        ubicaciones_sensores: Lista de sensores [[lat, lon], ...]
    
    Returns:
        float: Puntaje de distribución normalizado [0,1]
    """
    if len(ubicaciones_sensores) <= 1:
        return 1.0
    
    # Calcular todas las distancias entre pares de sensores
    distancias = []
    for i in range(len(ubicaciones_sensores)):
        for j in range(i + 1, len(ubicaciones_sensores)):
            dist = calcular_distancia(ubicaciones_sensores[i], ubicaciones_sensores[j])
            distancias.append(dist)
    
    dist_ideal = CONFIG['distancia_ideal']
    puntaje_dispersion = 0
    
    # Evaluar cada distancia contra la distancia ideal
    for dist in distancias:
        if dist >= dist_ideal * 0.7 and dist <= dist_ideal * 1.3:
            # Distancia cercana al ideal - puntaje completo
            puntaje_dispersion += 1
        else:
            # Puntaje reducido proporcionalmente a la desviación
            puntaje_dispersion += max(0, 1 - abs(dist - dist_ideal) / dist_ideal)
    
    return puntaje_dispersion / len(distancias)

def funcion_objetivo(ubicaciones_sensores, datos):
    """
    Función objetivo principal para el algoritmo PSO
    
    Combina múltiples criterios de optimización en un solo puntaje:
    - Cobertura espacial
    - Balance entre cultivos
    - Cobertura de zonas críticas
    - Distribución óptima
    
    Args:
        ubicaciones_sensores: Lista de sensores [[lat, lon], ...]
        datos: DataFrame con puntos de muestreo
    
    Returns:
        float: Puntaje total de la configuración [0,1]
    """
    # Calcular componentes individuales
    puntaje_cobertura = calcular_cobertura_variabilidad(ubicaciones_sensores, datos)
    puntaje_cultivos = balance_entre_cultivos(ubicaciones_sensores, datos)
    puntaje_criticas = cubrir_zonas_problematicas(ubicaciones_sensores, datos)
    puntaje_distribucion = optimizar_distancias(ubicaciones_sensores)
    
    # Combinar con pesos definidos en configuración
    pesos = CONFIG['pesos']
    puntaje_total = (pesos['cobertura'] * puntaje_cobertura + 
                     pesos['balance_cultivos'] * puntaje_cultivos + 
                     pesos['zonas_criticas'] * puntaje_criticas + 
                     pesos['distribucion'] * puntaje_distribucion)
    
    return puntaje_total