# Proyecto_PSO_riego_agricultura#  PSO Optimización de Riego Agrícola

**Sistema de inteligencia artificial para optimizar la ubicación de sensores de humedad en campos agrícolas usando algoritmo de Enjambre de Partículas (PSO)**

---

## Descripción

Este proyecto implementa un algoritmo de Optimización por Enjambre de Partículas (PSO) para determinar la ubicación óptima de sensores de humedad en campos agrícolas de la región de Guasave, Sinaloa. Utiliza **datos reales** de 100 puntos de muestreo con coordenadas geográficas exactas.

### Objetivo
Optimizar la distribución de sensores considerando:
- Cobertura espacial del área agrícola
- Balance entre diferentes tipos de cultivo
- Cobertura de zonas críticas (salinidad, humedad extrema)
- Distribución eficiente de sensores

---

## Características Principales

- ** Algoritmo PSO** implementado desde cero
- ** Datos reales** de Guasave, Sinaloa
- ** Función objetivo multi-criterio** (4 componentes ponderados)
- ** Visualizaciones avanzadas** para análisis de resultados
- ** Comparación con métodos manuales**
- ** Arquitectura modular** y extensible


## 🏗️ Estructura del Proyecto

proyecto_pso_riego/
├── main.py # Script principal
├── config.py # Parámetros globales
├── funciones_objetivo.py # Evaluación de soluciones
├── algoritmo_pso.py # Implementación PSO
├── visualizaciones.py # Gráficos y análisis
├── configuraciones.py # Estrategias manuales
└── README.md # Este archivo

# Parametros configurables En config.py 
PSO_CONFIG = {
    'inercia': 0.7,
    'cognitivo': 1.5,
    'social': 1.5,
    'particulas': 25,
    'iteraciones': 80
}