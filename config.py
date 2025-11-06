"""
Configuración global del proyecto PSO para optimización de riego
Parámetros y constantes utilizadas en todo el sistema
"""

# Parámetros de la función objetivo
CONFIG = {
    'radio_cobertura': 0.012,      # Radio de cobertura básica de sensores (grados)
    'radio_influencia': 0.018,     # Radio de influencia para balance de cultivos
    'distancia_ideal': 0.025,      # Distancia ideal entre sensores para optimizar distribución
    'pesos': {
        'cobertura': 0.35,         # Peso para cobertura espacial
        'balance_cultivos': 0.25,  # Peso para balance entre tipos de cultivo
        'zonas_criticas': 0.25,    # Peso para cobertura de zonas problemáticas
        'distribucion': 0.15       # Peso para distribución óptima de sensores
    },
    'humedad_ideal': {
        'Maíz': {'min': 30, 'max': 45, 'peso': 1.0},
        'Tomate': {'min': 25, 'max': 40, 'peso': 1.0},
        'Chile': {'min': 20, 'max': 35, 'peso': 1.0}
    }
}

# Parámetros del algoritmo PSO
PSO_CONFIG = {
    'inercia': 0.7,           # Parámetro de inercia (w)
    'cognitivo': 1.5,         # Parámetro cognitivo (c1)
    'social': 1.5,            # Parámetro social (c2)
    'velocidad_maxima': 0.005 # Límite de velocidad de partículas
}