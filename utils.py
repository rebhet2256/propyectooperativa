"""
Módulo de Utilidades para el Sistema de Optimización de Ayuda Humanitaria
Contiene validaciones, procesamiento de datos y funciones de visualización
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Tuple


class ValidadorDatos:
    """Valida los datos de entrada del usuario"""
    
    @staticmethod
    def validar_centro(nombre: str, oferta: float) -> Tuple[bool, str]:
        """Valida los datos de un centro de acopio"""
        if not nombre or not nombre.strip():
            return False, "El nombre del centro no puede estar vacío"
        if oferta <= 0:
            return False, "La oferta debe ser un número positivo"
        return True, ""
    
    @staticmethod
    def validar_zona(nombre: str, demanda: float) -> Tuple[bool, str]:
        """Valida los datos de una zona afectada"""
        if not nombre or not nombre.strip():
            return False, "El nombre de la zona no puede estar vacío"
        if demanda <= 0:
            return False, "La demanda debe ser un número positivo"
        return True, ""
    
    @staticmethod
    def validar_costo(costo: float) -> Tuple[bool, str]:
        """Valida un costo de transporte"""
        if costo < 0:
            return False, "El costo no puede ser negativo"
        return True, ""
    
    @staticmethod
    def validar_nombres_unicos(nombres: List[str], tipo: str) -> Tuple[bool, str]:
        """Valida que no haya nombres duplicados"""
        if len(nombres) != len(set(nombres)):
            duplicados = [n for n in nombres if nombres.count(n) > 1]
            return False, f"Nombres duplicados en {tipo}: {', '.join(set(duplicados))}"
        return True, ""


class GeneradorVisualizaciones:
    """Genera visualizaciones interactivas con Plotly"""
    
    @staticmethod
    def grafico_barras_por_zona(distribucion: Dict[str, float], 
                                 titulo: str = "Ayuda Enviada por Zona Afectada") -> go.Figure:
        """
        Genera un gráfico de barras mostrando cantidad de ayuda por zona.
        
        Args:
            distribucion: Diccionario {zona: cantidad_total}
            titulo: Título del gráfico
        
        Returns:
            Figura de Plotly
        """
        zonas = list(distribucion.keys())
        cantidades = list(distribucion.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=zonas,
                y=cantidades,
                marker=dict(
                    color=cantidades,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Cantidad")
                ),
                text=[f"{c:.0f}" for c in cantidades],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Cantidad: %{y:.0f} unidades<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=titulo,
            xaxis_title="Zonas Afectadas",
            yaxis_title="Cantidad de Ayuda (unidades)",
            template="plotly_white",
            hovermode='x unified',
            height=450
        )
        
        return fig
    
    @staticmethod
    def grafico_circular_centros(distribucion: Dict[str, float],
                                  titulo: str = "Participación de Centros de Acopio") -> go.Figure:
        """
        Genera un gráfico circular mostrando la participación de cada centro.
        
        Args:
            distribucion: Diccionario {centro: cantidad_total}
            titulo: Título del gráfico
        
        Returns:
            Figura de Plotly
        """
        centros = list(distribucion.keys())
        cantidades = list(distribucion.values())
        
        fig = go.Figure(data=[
            go.Pie(
                labels=centros,
                values=cantidades,
                hovertemplate='<b>%{label}</b><br>Cantidad: %{value:.0f} unidades<br>Porcentaje: %{percent}<extra></extra>',
                textposition='inside',
                textinfo='label+percent'
            )
        ])
        
        fig.update_layout(
            title=titulo,
            template="plotly_white",
            height=450
        )
        
        return fig
    
    @staticmethod
    def diagrama_sankey(solucion: List[Dict]) -> go.Figure:
        """
        Genera un diagrama de flujo Sankey mostrando el flujo de ayuda.
        
        Args:
            solucion: Lista de diccionarios con {Centro, Zona, Cantidad}
        
        Returns:
            Figura de Plotly con diagrama Sankey
        """
        df = pd.DataFrame(solucion)
        
        # Obtener listas únicas de centros y zonas
        centros = df['Centro'].unique().tolist()
        zonas = df['Zona'].unique().tolist()
        
        # Crear índices para nodos
        todos_nodos = centros + zonas
        indice_nodos = {nodo: idx for idx, nodo in enumerate(todos_nodos)}
        
        # Preparar fuentes, destinos y valores
        source = [indice_nodos[row['Centro']] for _, row in df.iterrows()]
        target = [indice_nodos[row['Zona']] for _, row in df.iterrows()]
        value = df['Cantidad'].tolist()
        
        # Definir colores para nodos
        colores_nodos = []
        for nodo in todos_nodos:
            if nodo in centros:
                colores_nodos.append('rgba(66, 139, 202, 0.8)')  # Azul para centros
            else:
                colores_nodos.append('rgba(220, 53, 69, 0.8)')   # Rojo para zonas
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='black', width=0.5),
                label=todos_nodos,
                color=colores_nodos
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                label=[f"{df.iloc[i]['Centro']} → {df.iloc[i]['Zona']}: {df.iloc[i]['Cantidad']:.0f}" 
                       for i in range(len(df))],
                color='rgba(200, 200, 200, 0.4)'
            )
        )])
        
        fig.update_layout(
            title="Diagrama de Flujo: Distribución de Ayuda Humanitaria (Sankey)",
            font=dict(size=10),
            height=600,
            template="plotly_white"
        )
        
        return fig
    
    @staticmethod
    def tabla_resultados(solucion: List[Dict]) -> pd.DataFrame:
        """
        Convierte la solución en un DataFrame formateado.
        
        Args:
            solucion: Lista de diccionarios con la solución
        
        Returns:
            DataFrame con formato
        """
        df = pd.DataFrame(solucion)
        
        if df.empty:
            return df
        
        # Renombrar columnas para mejor presentación
        df = df.rename(columns={
            'Centro': '🏢 Centro de Acopio',
            'Zona': '📍 Zona Afectada',
            'Cantidad': '📦 Cantidad (unidades)',
            'Costo_Unitario': '💰 Costo Unitario',
            'Costo_Total': '💵 Costo Total'
        })
        
        # Reordenar columnas
        orden = ['🏢 Centro de Acopio', '📍 Zona Afectada', '📦 Cantidad (unidades)', 
                 '💰 Costo Unitario', '💵 Costo Total']
        df = df[orden]
        
        return df


class FormateadorResultados:
    """Formatea los resultados para presentación"""
    
    @staticmethod
    def formatear_moneda(valor: float) -> str:
        """Formatea un valor numérico como moneda"""
        return f"${valor:,.2f}"
    
    @staticmethod
    def formatear_cantidad(valor: float) -> str:
        """Formatea una cantidad"""
        return f"{valor:,.2f}"
    
    @staticmethod
    def generar_resumen_texto(resumen: Dict) -> str:
        """
        Genera un texto resumido de los resultados.
        
        Args:
            resumen: Diccionario con datos de resumen
        
        Returns:
            Texto formateado con los resultados
        """
        texto = f"""
        ✅ **SOLUCIÓN ÓPTIMA ENCONTRADA**
        
        📊 **Estadísticas Generales:**
        - **Costo Total Mínimo:** ${resumen['costo_total']:,.2f}
        - **Cantidad Total Transportada:** {resumen['cantidad_total_transportada']:,.0f} unidades
        - **Rutas Utilizadas:** {resumen['cantidad_rutas_usadas']} rutas
        
        🏢 **Centros de Acopio Utilizados:** {', '.join(resumen['centros_utilizados'])}
        
        📍 **Zonas Atendidas:** {', '.join(resumen['zonas_atendidas'])}
        """
        return texto
    
    @staticmethod
    def generar_desglose_centros(distribucion: Dict[str, float]) -> str:
        """Genera desglose de distribución por centros"""
        texto = "**Distribución por Centro de Acopio:**\n\n"
        for centro, cantidad in sorted(distribucion.items()):
            texto += f"- **{centro}:** {cantidad:,.0f} unidades\n"
        return texto
    
    @staticmethod
    def generar_desglose_zonas(distribucion: Dict[str, float]) -> str:
        """Genera desglose de distribución por zonas"""
        texto = "**Distribución por Zona Afectada:**\n\n"
        for zona, cantidad in sorted(distribucion.items()):
            texto += f"- **{zona}:** {cantidad:,.0f} unidades\n"
        return texto


class GeneradorModelo:
    """Genera representaciones del modelo matemático"""
    
    @staticmethod
    def generar_descripcion_modelo() -> str:
        """Genera la descripción matemática del modelo"""
        return """
        ## 📐 Modelo Matemático de Transporte
        
        ### Formulación
        
        **Función Objetivo:**
        ```
        Minimizar Z = ∑∑ Cᵢⱼ · Xᵢⱼ
        ```
        
        Donde:
        - **Z** = Costo total de transporte a minimizar
        - **Cᵢⱼ** = Costo unitario de transportar desde el centro *i* a la zona *j*
        - **Xᵢⱼ** = Cantidad de ayuda transportada desde el centro *i* a la zona *j*
        
        ### Restricciones
        
        **1. Restricciones de Oferta (No exceder disponibilidad):**
        ```
        ∑ⱼ Xᵢⱼ ≤ Sᵢ    ∀i ∈ Centros
        ```
        - Donde **Sᵢ** es la oferta disponible del centro *i*
        
        **2. Restricciones de Demanda (Satisfacer necesidad):**
        ```
        ∑ᵢ Xᵢⱼ ≥ Dⱼ    ∀j ∈ Zonas
        ```
        - Donde **Dⱼ** es la demanda requerida de la zona *j*
        
        **3. Restricciones de No Negatividad:**
        ```
        Xᵢⱼ ≥ 0    ∀i,j
        ```
        
        ### Método de Solución
        
        El modelo se resuelve mediante:
        - **Programación Lineal** (LP)
        - **Método Simplex** implementado en PuLP
        - **Solver CBC** (Coin-or-Branch and Cut)
        
        ### Interpretación
        
        La solución óptima proporciona:
        - La cantidad exacta a transportar en cada ruta
        - El costo mínimo total garantizado
        - Una estrategia de distribución eficiente
        """
