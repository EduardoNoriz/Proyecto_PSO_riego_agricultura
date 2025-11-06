"""
Algoritmo de Optimización por Enjambre de Partículas (PSO)
Implementación especializada para el problema de ubicación de sensores
"""

import numpy as np
from config import PSO_CONFIG 
from funciones_objetivo import funcion_objetivo

class PSOOptimizer:
    """
    Clase que implementa el algoritmo PSO para optimizar ubicación de sensores
    
    Atributos:
        datos: DataFrame con los puntos de muestreo
        n_sensores: Número de sensores a ubicar
        n_particulas: Tamaño del enjambre
        max_iter: Número máximo de iteraciones
        particulas: Posiciones actuales del enjambre
        velocidades: Velocidades actuales del enjambre
        mejores_locales: Mejores posiciones individuales
        mejor_global: Mejor posición global encontrada
    """
    
    def __init__(self, datos, n_sensores=5, n_particulas=30, max_iter=100):
        """
        Inicializar el optimizador PSO
        
        Args:
            datos: DataFrame con datos de cultivos
            n_sensores: Número de sensores a optimizar
            n_particulas: Tamaño del enjambre de partículas
            max_iter: Número máximo de iteraciones
        """
        self.datos = datos
        self.n_sensores = n_sensores
        self.n_particulas = n_particulas
        self.max_iter = max_iter
        
        # Establecer límites del espacio de búsqueda
        self.lat_min, self.lat_max = datos['Latitud'].min(), datos['Latitud'].max()
        self.lon_min, self.lon_max = datos['Longitud'].min(), datos['Longitud'].max()
        
        # Cargar parámetros PSO desde configuración
        self.w = PSO_CONFIG['inercia']
        self.c1 = PSO_CONFIG['cognitivo']
        self.c2 = PSO_CONFIG['social']
        self.vel_max = PSO_CONFIG['velocidad_maxima']
        
        # Inicializar estado del algoritmo
        self._inicializar_enjambre()
        
        # Historial para análisis de convergencia
        self.historial_puntajes = []
    
    def _inicializar_enjambre(self):
        """
        Inicializar las posiciones y velocidades del enjambre
        
        Cada partícula representa una posible configuración de sensores
        Formato: [lat1, lon1, lat2, lon2, ..., latN, lonN]
        """
        # Inicializar posiciones aleatorias dentro de los límites
        self.particulas = self._inicializar_particulas()
        self.velocidades = self._inicializar_velocidades()
        
        # Inicializar mejores posiciones individuales
        self.mejores_locales = self.particulas.copy()
        self.mejores_puntajes_locales = [self._evaluar_particula(p) for p in self.particulas]
        
        # Encontrar mejor posición global inicial
        mejor_idx = np.argmax(self.mejores_puntajes_locales)
        self.mejor_global = self.particulas[mejor_idx].copy()
        self.mejor_puntaje_global = self.mejores_puntajes_locales[mejor_idx]
    
    def _inicializar_particulas(self):
        """
        Crear partículas con posiciones aleatorias dentro del espacio de búsqueda
        
        Returns:
            list: Lista de arrays numpy representando las partículas
        """
        particulas = []
        for _ in range(self.n_particulas):
            particula = []
            for _ in range(self.n_sensores):
                # Generar coordenadas aleatorias dentro de los límites geográficos
                lat = np.random.uniform(self.lat_min, self.lat_max)
                lon = np.random.uniform(self.lon_min, self.lon_max)
                particula.extend([lat, lon])
            particulas.append(np.array(particula))
        return particulas
    
    def _inicializar_velocidades(self):
        """
        Inicializar velocidades con valores pequeños aleatorios
        
        Returns:
            list: Lista de arrays numpy representando las velocidades
        """
        velocidades = []
        for _ in range(self.n_particulas):
            # Velocidades iniciales pequeñas para exploración gradual
            velocidad = np.random.uniform(-0.001, 0.001, self.n_sensores * 2)
            velocidades.append(velocidad)
        return velocidades
    
    def _formatear_sensores(self, particula):
        """
        Convertir representación de partícula a lista de sensores
        
        Args:
            particula: Array numpy con formato [lat1, lon1, lat2, lon2, ...]
        
        Returns:
            list: Lista de sensores [[lat, lon], ...]
        """
        return [particula[i:i+2].tolist() for i in range(0, len(particula), 2)]
    
    def _evaluar_particula(self, particula):
        """
        Evaluar una partícula usando la función objetivo
        
        Args:
            particula: Array numpy representando una configuración de sensores
        
        Returns:
            float: Puntaje de la configuración según función objetivo
        """
        sensores = self._formatear_sensores(particula)
        return funcion_objetivo(sensores, self.datos)
    
    def optimizar(self):
        """
        Ejecutar el algoritmo PSO para encontrar configuración óptima
        
        Returns:
            tuple: (mejores_sensores, mejor_puntaje) - Configuración óptima encontrada
        """
        print(f"Iniciando PSO - {self.n_particulas} particulas, {self.max_iter} iteraciones")
        
        for iteracion in range(self.max_iter):
            # Evaluar y actualizar mejores posiciones
            self._actualizar_mejores_posiciones()
            
            # Mover partículas según ecuaciones de PSO
            self._actualizar_velocidades_posiciones()
            
            # Registrar progreso
            self.historial_puntajes.append(self.mejor_puntaje_global)
            
            # Mostrar progreso cada 10 iteraciones
            if (iteracion + 1) % 10 == 0:
                print(f"Iteracion {iteracion + 1}: Mejor puntaje = {self.mejor_puntaje_global:.4f}")
        
        print("Optimizacion completada")
        print(f"Mejor puntaje encontrado: {self.mejor_puntaje_global:.4f}")
        
        return self._formatear_sensores(self.mejor_global), self.mejor_puntaje_global
    
    def _actualizar_mejores_posiciones(self):
        """
        Actualizar mejores posiciones locales y globales
        """
        for i in range(self.n_particulas):
            # Evaluar partícula actual
            puntaje_actual = self._evaluar_particula(self.particulas[i])
            
            # Actualizar mejor local si se encontró mejora
            if puntaje_actual > self.mejores_puntajes_locales[i]:
                self.mejores_puntajes_locales[i] = puntaje_actual
                self.mejores_locales[i] = self.particulas[i].copy()
            
            # Actualizar mejor global si se encontró mejora
            if puntaje_actual > self.mejor_puntaje_global:
                self.mejor_puntaje_global = puntaje_actual
                self.mejor_global = self.particulas[i].copy()
    
    def _actualizar_velocidades_posiciones(self):
        """
        Actualizar velocidades y posiciones según ecuaciones de PSO
        """
        for i in range(self.n_particulas):
            # Generar factores aleatorios para estocasticidad
            r1, r2 = np.random.random(2)
            
            # Calcular componentes de velocidad
            inercia = self.w * self.velocidades[i]
            cognitivo = self.c1 * r1 * (self.mejores_locales[i] - self.particulas[i])
            social = self.c2 * r2 * (self.mejor_global - self.particulas[i])
            
            # Actualizar velocidad total
            self.velocidades[i] = inercia + cognitivo + social
            
            # Limitar velocidad máxima para estabilidad
            self.velocidades[i] = np.clip(self.velocidades[i], -self.vel_max, self.vel_max)
            
            # Actualizar posición
            self.particulas[i] += self.velocidades[i]
            
            # Aplicar restricciones de límites geográficos
            self._aplicar_restricciones(i)
    
    def _aplicar_restricciones(self, indice_particula):
        """
        Asegurar que las partículas se mantengan dentro de los límites geográficos
        
        Args:
            indice_particula: Índice de la partícula a restringir
        """
        for j in range(0, len(self.particulas[indice_particula]), 2):
            # Restringir latitud
            self.particulas[indice_particula][j] = np.clip(
                self.particulas[indice_particula][j], self.lat_min, self.lat_max
            )
            # Restringir longitud
            self.particulas[indice_particula][j+1] = np.clip(
                self.particulas[indice_particula][j+1], self.lon_min, self.lon_max
            )
    
    def visualizar_convergencia(self):
        """
        Visualizar la convergencia del algoritmo a lo largo de las iteraciones
        """
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        plt.plot(self.historial_puntajes, linewidth=2)
        plt.xlabel('Iteracion')
        plt.ylabel('Mejor Puntaje')
        plt.title('Convergencia del Algoritmo PSO')
        plt.grid(True, alpha=0.3)
        plt.show()