"""
Sistema de Optimización del Transporte de Ayuda Humanitaria en Desastres Naturales
Aplicación Streamlit para optimización de distribución logística
UMSA - Investigación Operativa
"""

import streamlit as st
import pandas as pd
import numpy as np
from transporte import ModeloTransporte
from utils import (ValidadorDatos, GeneradorVisualizaciones, 
                   FormateadorResultados, GeneradorModelo)


# Configuración de la página
st.set_page_config(
    page_title="Sistema de Optimización de Ayuda Humanitaria",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .titulo-principal {
        text-align: center;
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subtitulo {
        text-align: center;
        color: #555;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .card {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 20px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)


def inicializar_sesion():
    """Inicializa las variables de sesión necesarias"""
    if 'centros' not in st.session_state:
        st.session_state.centros = {}
    if 'demandas' not in st.session_state:
        st.session_state.demandas = {}
    if 'matriz_costos' not in st.session_state:
        st.session_state.matriz_costos = None
    if 'solucion' not in st.session_state:
        st.session_state.solucion = None
    if 'resumen' not in st.session_state:
        st.session_state.resumen = None


def pagina_inicio():
    """Página de bienvenida e introducción"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="titulo-principal">🚛 Sistema de Optimización</div>', 
                   unsafe_allow_html=True)
        st.markdown(
            '<div class="titulo-principal" style="font-size:1.8em; color:#dc3545;">del Transporte de Ayuda Humanitaria</div>', 
            unsafe_allow_html=True
        )
    
    st.markdown('<div class="subtitulo">En Desastres Naturales</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ## 🎯 Objetivo del Sistema
        
        Desarrollar una herramienta que permita **optimizar la distribución de ayuda humanitaria** 
        desde centros de acopio hacia zonas afectadas por desastres naturales, 
        **minimizando costos de transporte** mediante el uso de **Programación Lineal** y el 
        **Modelo de Transporte**.
        
        Este sistema busca:
        - ✅ Minimizar costos totales de transporte
        - ✅ Satisfacer demandas de zonas afectadas
        - ✅ Optimizar uso de recursos disponibles
        - ✅ Proporcionar decisiones basadas en datos
        """)
    
    with col2:
        st.markdown("""
        ## 📦 Modelo de Transporte
        
        El **Modelo de Transporte** es un caso especial de Programación Lineal que resuelve 
        problemas de distribución óptima de recursos desde múltiples fuentes hacia múltiples destinos.
        
        **Características:**
        - Minimiza el costo total de distribución
        - Respeta las restricciones de oferta
        - Satisface las restricciones de demanda
        - Utiliza el **Método Simplex** para optimización
        - Garantiza soluciones óptimas en tiempo polinomial
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ## 🌍 Importancia de la Logística Humanitaria
    
    Durante desastres naturales, la **logística eficiente** es crítica:
    
    | Aspecto | Importancia |
    |--------|-----------|
    | **Tiempo** | Cada minuto cuenta para salvar vidas |
    | **Costo** | Recursos limitados deben utilizarse eficientemente |
    | **Cobertura** | Todas las zonas afectadas deben recibir ayuda |
    | **Equidad** | Distribución justa según necesidad |
    | **Sostenibilidad** | Optimizar para múltiples fases de desastre |
    
    Este sistema utiliza **métodos científicos** para tomar decisiones logísticas óptimas.
    """)
    
    st.markdown("---")
    
    st.info("""
    👉 **Instrucciones de Uso:**
    1. Registra los **Centros de Acopio** disponibles y su oferta
    2. Registra las **Zonas Afectadas** y sus demandas
    3. Ingresa la **Matriz de Costos** de transporte
    4. Presiona **"Calcular Solución Óptima"** para obtener la distribución
    5. Visualiza los **Resultados y Gráficos** de la solución
    """)


def pagina_configuracion():
    """Página para configurar centros, demandas y costos"""
    st.header("⚙️ Configuración del Problema")
    
    tab1, tab2, tab3 = st.tabs(["🏢 Centros de Acopio", "📍 Zonas Afectadas", "💰 Matriz de Costos"])
    
    # TAB 1: Centros de Acopio
    with tab1:
        st.subheader("Registrar Centros de Acopio")
        st.write("Define los centros de distribución y su oferta disponible")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nombre_centro = st.text_input(
                "Nombre del centro",
                key="input_centro",
                placeholder="Ej: La Paz"
            )
        
        with col2:
            oferta = st.number_input(
                "Oferta (unidades)",
                min_value=0.0,
                value=100.0,
                step=10.0,
                key="input_oferta"
            )
        
        with col3:
            if st.button("➕ Agregar Centro", use_container_width=True):
                # Validar
                valido, msg = ValidadorDatos.validar_centro(nombre_centro, oferta)
                if not valido:
                    st.error(msg)
                elif nombre_centro in st.session_state.centros:
                    st.error("⚠️ Este centro ya existe")
                else:
                    st.session_state.centros[nombre_centro] = oferta
                    st.success(f"✅ Centro '{nombre_centro}' agregado con oferta {oferta}")
                    st.rerun()
        
        if st.session_state.centros:
            st.subheader("Centros Registrados")
            
            df_centros = pd.DataFrame([
                {"Centro": nombre, "Oferta": oferta}
                for nombre, oferta in st.session_state.centros.items()
            ])
            
            st.dataframe(df_centros, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                centro_eliminar = st.selectbox(
                    "Eliminar centro",
                    ["Seleccionar..."] + list(st.session_state.centros.keys()),
                    key="select_eliminar_centro"
                )
                if centro_eliminar != "Seleccionar..." and st.button("🗑️ Eliminar", key="btn_eliminar_centro"):
                    del st.session_state.centros[centro_eliminar]
                    st.success(f"Centro '{centro_eliminar}' eliminado")
                    st.rerun()
            
            with col2:
                st.metric("Total Centros", len(st.session_state.centros))
                st.metric("Oferta Total", sum(st.session_state.centros.values()))
        else:
            st.info("📌 Añade al menos un centro para comenzar")
    
    # TAB 2: Zonas Afectadas
    with tab2:
        st.subheader("Registrar Zonas Afectadas")
        st.write("Define las zonas que requieren ayuda y su demanda")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            nombre_zona = st.text_input(
                "Nombre de la zona",
                key="input_zona",
                placeholder="Ej: Beni"
            )
        
        with col2:
            demanda = st.number_input(
                "Demanda (unidades)",
                min_value=0.0,
                value=100.0,
                step=10.0,
                key="input_demanda"
            )
        
        with col3:
            if st.button("➕ Agregar Zona", use_container_width=True):
                valido, msg = ValidadorDatos.validar_zona(nombre_zona, demanda)
                if not valido:
                    st.error(msg)
                elif nombre_zona in st.session_state.demandas:
                    st.error("⚠️ Esta zona ya existe")
                else:
                    st.session_state.demandas[nombre_zona] = demanda
                    st.success(f"✅ Zona '{nombre_zona}' agregada con demanda {demanda}")
                    st.rerun()
        
        if st.session_state.demandas:
            st.subheader("Zonas Registradas")
            
            df_zonas = pd.DataFrame([
                {"Zona": nombre, "Demanda": demanda}
                for nombre, demanda in st.session_state.demandas.items()
            ])
            
            st.dataframe(df_zonas, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                zona_eliminar = st.selectbox(
                    "Eliminar zona",
                    ["Seleccionar..."] + list(st.session_state.demandas.keys()),
                    key="select_eliminar_zona"
                )
                if zona_eliminar != "Seleccionar..." and st.button("🗑️ Eliminar", key="btn_eliminar_zona"):
                    del st.session_state.demandas[zona_eliminar]
                    st.success(f"Zona '{zona_eliminar}' eliminada")
                    st.rerun()
            
            with col2:
                st.metric("Total Zonas", len(st.session_state.demandas))
                st.metric("Demanda Total", sum(st.session_state.demandas.values()))
        else:
            st.info("📌 Añade al menos una zona para comenzar")
    
    # TAB 3: Matriz de Costos
    with tab3:
        if not st.session_state.centros or not st.session_state.demandas:
            st.warning("⚠️ Primero debes registrar centros y zonas")
        else:
            st.subheader("Ingresar Matriz de Costos de Transporte")
            st.write("Especifica el costo unitario de transportar desde cada centro a cada zona")
            
            # Crear o cargar matriz
            if st.session_state.matriz_costos is None:
                st.session_state.matriz_costos = np.ones((
                    len(st.session_state.centros),
                    len(st.session_state.demandas)
                ))
            
            centros_lista = list(st.session_state.centros.keys())
            zonas_lista = list(st.session_state.demandas.keys())
            
            # Crear DataFrame editable
            df_costos = pd.DataFrame(
                st.session_state.matriz_costos,
                index=centros_lista,
                columns=zonas_lista
            )
            
            st.write("**Editar costos de transporte:**")
            df_editada = st.data_editor(
                df_costos,
                num_rows="fixed",
                use_container_width=True,
                key="editor_matriz_costos"
            )
            
            # Actualizar matriz en sesión
            st.session_state.matriz_costos = df_editada.values
            
            # Mostrar matriz en forma de tabla
            st.subheader("Vista Previa de la Matriz")
            st.table(df_editada)
            
            # Estadísticas de costos
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Costo Mínimo", f"${df_editada.values.min():.2f}")
            with col2:
                st.metric("Costo Máximo", f"${df_editada.values.max():.2f}")
            with col3:
                st.metric("Costo Promedio", f"${df_editada.values.mean():.2f}")
            with col4:
                st.metric("Desv. Estándar", f"${df_editada.values.std():.2f}")


def pagina_modelo():
    """Página mostrando el modelo matemático"""
    st.header("📐 Formulación Matemática")
    
    st.markdown(GeneradorModelo.generar_descripcion_modelo())
    
    # Mostrar ejemplo con datos actuales si existen
    if st.session_state.centros and st.session_state.demandas:
        st.markdown("---")
        st.subheader("📋 Ejemplo con tus Datos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Centros de Acopio (Oferta):**")
            for centro, oferta in st.session_state.centros.items():
                st.write(f"- S({centro}) = {oferta} unidades")
        
        with col2:
            st.markdown("**Zonas Afectadas (Demanda):**")
            for zona, demanda in st.session_state.demandas.items():
                st.write(f"- D({zona}) = {demanda} unidades")
        
        st.markdown("**Matriz de Costos:**")
        if st.session_state.matriz_costos is not None:
            df_costos = pd.DataFrame(
                st.session_state.matriz_costos,
                index=list(st.session_state.centros.keys()),
                columns=list(st.session_state.demandas.keys())
            )
            st.table(df_costos)


def pagina_optimizacion():
    """Página de optimización y resultados"""
    st.header("⚡ Optimización y Resultados")
    
    # Validar que tenemos datos
    if not st.session_state.centros or not st.session_state.demandas or st.session_state.matriz_costos is None:
        st.error("❌ Debes completar la configuración antes de optimizar")
        st.info("Ve a la pestaña 'Configuración' para agregar datos")
        return
    
    # Botón para calcular solución
    if st.button("🚀 Calcular Solución Óptima", use_container_width=True, type="primary"):
        with st.spinner("⏳ Optimizando distribución de ayuda..."):
            # Crear modelo
            modelo = ModeloTransporte(
                centros=st.session_state.centros,
                demandas=st.session_state.demandas,
                costos=st.session_state.matriz_costos,
                nombres_filas=list(st.session_state.centros.keys()),
                nombres_columnas=list(st.session_state.demandas.keys())
            )
            
            # Validar entrada
            valido, msg = modelo.validar_entrada()
            if not valido:
                st.error(f"❌ Error de validación: {msg}")
                return
            
            # Construir y resolver
            modelo.construir_modelo()
            resultado = modelo.resolver()
            
            if resultado['estado'] != 'Optimal':
                st.error(f"❌ {resultado['mensaje']}")
                return
            
            # Guardar resultados en sesión
            st.session_state.solucion = resultado['distribucion']
            st.session_state.resumen = modelo.obtener_resumen()
            
            st.success("✅ ¡Solución óptima encontrada!")
    
    # Mostrar resultados si existen
    if st.session_state.solucion:
        st.markdown("---")
        
        # Resumen general
        resumen = st.session_state.resumen
        
        st.markdown(FormateadorResultados.generar_resumen_texto(resumen), unsafe_allow_html=False)
        
        # Detalles de distribución
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(FormateadorResultados.generar_desglose_centros(resumen['distribucion_por_centro']))
        
        with col2:
            st.markdown(FormateadorResultados.generar_desglose_zonas(resumen['distribucion_por_zona']))
        
        st.markdown("---")
        
        # Tabla de resultados detallada
        st.subheader("📊 Tabla Detallada de Distribución")
        
        df_resultados = GeneradorVisualizaciones.tabla_resultados(st.session_state.solucion)
        st.dataframe(df_resultados, use_container_width=True, hide_index=True)
        
        # Descargar resultados
        csv = df_resultados.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar resultados (CSV)",
            data=csv,
            file_name="solucion_distribucion.csv",
            mime="text/csv"
        )


def pagina_graficos():
    """Página con visualizaciones de resultados"""
    st.header("📈 Visualizaciones")
    
    if not st.session_state.solucion:
        st.info("📊 Primero calcula la solución óptima en la pestaña 'Optimización'")
        return
    
    resumen = st.session_state.resumen
    
    # Gráfico 1: Barras por zona
    st.subheader("Ayuda Enviada por Zona Afectada")
    fig1 = GeneradorVisualizaciones.grafico_barras_por_zona(
        resumen['distribucion_por_zona']
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Gráfico 2: Circular de participación
    st.subheader("Participación de Centros de Acopio")
    fig2 = GeneradorVisualizaciones.grafico_circular_centros(
        resumen['distribucion_por_centro']
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Gráfico 3: Sankey
    st.subheader("Diagrama de Flujo: Red de Distribución (Sankey)")
    fig3 = GeneradorVisualizaciones.diagrama_sankey(st.session_state.solucion)
    st.plotly_chart(fig3, use_container_width=True)


def main():
    """Función principal"""
    inicializar_sesion()
    
    # Barra lateral con navegación
    with st.sidebar:
       # st.image(None, use_column_width=True)
        st.markdown("# 🎓 UMSA")
        st.markdown("**Investigación Operativa**")
        st.markdown("---")
        
        pagina_actual = st.radio(
            "Navegación",
            ["🏠 Inicio", "⚙️ Configuración", "📐 Modelo", "⚡ Optimización", "📈 Gráficos"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("""
        ### 📋 Información
        
        **Proyecto:** Sistema de Optimización del Transporte de Ayuda Humanitaria
        
        **Universidad:** UMSA
        
        **Materia:** Investigación Operativa
        
        **Método:** Modelo de Transporte, Programación Lineal, Método Simplex
        """)
    
    # Contenido principal según página seleccionada
    if "Inicio" in pagina_actual:
        pagina_inicio()
    elif "Configuración" in pagina_actual:
        pagina_configuracion()
    elif "Modelo" in pagina_actual:
        pagina_modelo()
    elif "Optimización" in pagina_actual:
        pagina_optimizacion()
    elif "Gráficos" in pagina_actual:
        pagina_graficos()


if __name__ == "__main__":
    main()
