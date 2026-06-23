"""
Módulo de Modelo de Transporte para Optimización de Ayuda Humanitaria
Autor: Sistema de Optimización de Transporte
"""

import numpy as np
import pandas as pd
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpStatus
from typing import Dict, Tuple, List


class ModeloTransporte:
    """
    Implementa el Modelo de Transporte para optimizar la distribución
    de ayuda humanitaria desde centros de acopio hacia zonas afectadas.
    
    El modelo utiliza Programación Lineal y resuelve mediante el método Simplex
    a través de la librería PuLP.
    """
    
    def __init__(self, centros: Dict[str, float], demandas: Dict[str, float], 
                 costos: np.ndarray, nombres_filas: List[str], nombres_columnas: List[str]):
        """
        Inicializa el modelo de transporte.
        
        Args:
            centros: Diccionario {nombre_centro: oferta}
            demandas: Diccionario {nombre_zona: demanda}
            costos: Matriz numpy de costos de transporte
            nombres_filas: Lista de nombres de centros de acopio
            nombres_columnas: Lista de nombres de zonas afectadas
        """
        self.centros = centros
        self.demandas = demandas
        self.costos = costos
        self.nombres_filas = nombres_filas
        self.nombres_columnas = nombres_columnas
        self.problema = None
        self.variables = None
        self.solucion = None
        self.costo_total = None
        
    def construir_modelo(self) -> LpProblem:
        """
        Construye el modelo de programación lineal.
        
        Minimiza: Z = ∑∑ Cij * Xij
        
        Sujeto a:
            - ∑j Xij ≤ Si (oferta del centro i)
            - ∑i Xij ≥ Dj (demanda de la zona j)
            - Xij ≥ 0 (no negatividad)
        
        Returns:
            Problema PuLP configurado
        """
        # Crear el problema de minimización
        self.problema = LpProblem("Optimizacion_Ayuda_Humanitaria", LpMinimize)
        
        # Variables de decisión: Xij = cantidad transportada del centro i a zona j
        self.variables = {}
        for i, centro in enumerate(self.nombres_filas):
            for j, zona in enumerate(self.nombres_columnas):
                self.variables[(i, j)] = LpVariable(
                    f"X_{centro}_{zona}", 
                    lowBound=0, 
                    cat='Continuous'
                )
        
        # Función objetivo: Minimizar costo total
        self.problema += lpSum(
            self.costos[i, j] * self.variables[(i, j)]
            for i in range(len(self.nombres_filas))
            for j in range(len(self.nombres_columnas))
        ), "Costo_Total"
        
        # Restricciones de oferta (no se puede enviar más de lo disponible)
        for i, centro in enumerate(self.nombres_filas):
            self.problema += (
                lpSum(self.variables[(i, j)] for j in range(len(self.nombres_columnas))) 
                <= self.centros[centro],
                f"Oferta_{centro}"
            )
        
        # Restricciones de demanda (se debe satisfacer la demanda)
        for j, zona in enumerate(self.nombres_columnas):
            self.problema += (
                lpSum(self.variables[(i, j)] for i in range(len(self.nombres_filas))) 
                >= self.demandas[zona],
                f"Demanda_{zona}"
            )
        
        return self.problema
    
    def resolver(self) -> Dict:
        """
        Resuelve el modelo usando el método Simplex.
        
        Returns:
            Diccionario con resultados de la optimización
        """
        # Resolver el problema
        self.problema.solve()
        
        # Verificar estado de la solución
        estado = LpStatus[self.problema.status]
        
        if estado != 'Optimal':
            return {
                'estado': estado,
                'costo_total': None,
                'distribucion': None,
                'mensaje': f"No se encontró solución óptima. Estado: {estado}"
            }
        
        # Extraer la solución
        self.costo_total = self.problema.objective.value()
        distribucion = []
        
        for i, centro in enumerate(self.nombres_filas):
            for j, zona in enumerate(self.nombres_columnas):
                cantidad = self.variables[(i, j)].varValue
                
                # Solo incluir rutas con cantidad > 0.01 (evitar errores de precisión)
                if cantidad is not None and cantidad > 0.01:
                    distribucion.append({
                        'Centro': centro,
                        'Zona': zona,
                        'Cantidad': round(cantidad, 2),
                        'Costo_Unitario': self.costos[i, j],
                        'Costo_Total': round(cantidad * self.costos[i, j], 2)
                    })
        
        self.solucion = distribucion
        
        return {
            'estado': estado,
            'costo_total': round(self.costo_total, 2),
            'distribucion': distribucion,
            'mensaje': 'Solución óptima encontrada exitosamente'
        }
    
    def obtener_resumen(self) -> Dict:
        """
        Genera un resumen de los resultados de la optimización.
        
        Returns:
            Diccionario con estadísticas de la solución
        """
        if self.solucion is None:
            return None
        
        df = pd.DataFrame(self.solucion)
        
        resumen = {
            'costo_total': self.costo_total,
            'cantidad_rutas_usadas': len(self.solucion),
            'cantidad_total_transportada': df['Cantidad'].sum(),
            'centros_utilizados': df['Centro'].unique().tolist(),
            'zonas_atendidas': df['Zona'].unique().tolist(),
            'distribucion_por_centro': df.groupby('Centro')['Cantidad'].sum().to_dict(),
            'distribucion_por_zona': df.groupby('Zona')['Cantidad'].sum().to_dict(),
        }
        
        return resumen
    
    def obtener_matriz_distribucion(self) -> pd.DataFrame:
        """
        Retorna la matriz de distribución óptima.
        
        Returns:
            DataFrame con la matriz de flujos
        """
        if self.solucion is None:
            return None
        
        df = pd.DataFrame(self.solucion)
        
        # Crear matriz pivote
        matriz = df.pivot_table(
            index='Centro',
            columns='Zona',
            values='Cantidad',
            fill_value=0
        )
        
        return matriz.reindex(
            index=self.nombres_filas,
            columns=self.nombres_columnas,
            fill_value=0
        )
    
    def validar_entrada(self) -> Tuple[bool, str]:
        """
        Valida que los datos de entrada sean consistentes.
        
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        # Validar oferta
        oferta_total = sum(self.centros.values())
        if oferta_total <= 0:
            return False, "La oferta total debe ser positiva"
        
        # Validar demanda
        demanda_total = sum(self.demandas.values())
        if demanda_total <= 0:
            return False, "La demanda total debe ser positiva"
        
        # Validar que oferta >= demanda (problema balanceado)
        if oferta_total < demanda_total:
            return False, f"Oferta insuficiente. Oferta: {oferta_total}, Demanda: {demanda_total}"
        
        # Validar dimensiones de matriz de costos
        if self.costos.shape[0] != len(self.nombres_filas):
            return False, f"Filas en matriz de costos no coinciden con centros"
        
        if self.costos.shape[1] != len(self.nombres_columnas):
            return False, f"Columnas en matriz de costos no coinciden con zonas"
        
        # Validar que costos sean positivos
        if (self.costos < 0).any():
            return False, "Los costos no pueden ser negativos"
        
        return True, "Entrada válida"
