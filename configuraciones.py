"""
Módulo con configuraciones predefinidas para ubicación de sensores
Estrategias manuales para comparación con el algoritmo PSO
"""

import numpy as np
import pandas as pd

def configuracion_aleatoria(n_sensores=5, datos=None):
    """
    Generar configuración aleatoria de sensores
    
    Args:
        n_sensores: Número de sensores
        datos: DataFrame con datos para determinar límites
    
    Returns:
        list: Lista de sensores [[lat, lon], ...]
    """
    lat_min, lat_max = datos['Latitud'].min(), datos['Latitud'].max()
    lon_min, lon_max = datos['Longitud'].min(), datos['Longitud'].max()
    
    return [[np.random.uniform(lat_min, lat_max), 
             np.random.uniform(lon_min, lon_max)] for _ in range(n_sensores)]

def configuracion_centros_cultivo(n_sensores=5, datos=None):
    """
    Ubicar sensores en centros de masa de cada tipo de cultivo
    
    Args:
        n_sensores: Número de sensores
        datos: DataFrame con datos de cultivos
    
    Returns:
        list: Lista de sensores [[lat, lon], ...]
    """
    centros = {}
    for cultivo in ['Maíz', 'Tomate', 'Chile']:
        cultivo_data = datos[datos['Cultivo'] == cultivo]
        centros[cultivo] = [cultivo_data['Latitud'].mean(), cultivo_data['Longitud'].mean()]
    
    # Empezar con centros de cada cultivo
    sensores = [centros['Maíz'], centros['Tomate'], centros['Chile']]
    
    # Completar con variaciones alrededor de centros si se necesitan más sensores
    while len(sensores) < n_sensores:
        cultivo = np.random.choice(['Maíz', 'Tomate', 'Chile'])
        variacion_lat = np.random.uniform(-0.005, 0.005)
        variacion_lon = np.random.uniform(-0.005, 0.005)
        sensores.append([centros[cultivo][0] + variacion_lat,
                        centros[cultivo][1] + variacion_lon])
    
    return sensores

def configuracion_zonas_criticas(n_sensores=5, datos=None):
    """
    Ubicar sensores en zonas con problemas identificados
    
    Args:
        n_sensores: Número de sensores
        datos: DataFrame con datos de cultivos
    
    Returns:
        list: Lista de sensores [[lat, lon], ...]
    """
    # Identificar zonas críticas
    zonas_criticas = datos[
        (datos['Salinidad'] > 2.5) | 
        (datos['Humedad'] < 15) | 
        (datos['Humedad'] > 40)
    ]
    
    sensores = []
    if len(zonas_criticas) >= n_sensores:
        # Tomar los puntos más críticos (mayor salinidad)
        indices_criticos = zonas_criticas.nlargest(n_sensores, 'Salinidad').index
        for idx in indices_criticos:
            sensores.append([datos.loc[idx, 'Latitud'], datos.loc[idx, 'Longitud']])
    else:
        # Usar todas las zonas críticas disponibles
        for idx in zonas_criticas.index:
            sensores.append([datos.loc[idx, 'Latitud'], datos.loc[idx, 'Longitud']])
        # Completar con sensores aleatorios
        while len(sensores) < n_sensores:
            sensores.extend(configuracion_aleatoria(n_sensores - len(sensores), datos))
    
    return sensores