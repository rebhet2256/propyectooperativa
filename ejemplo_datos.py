"""
Datos de Ejemplo para Pruebas Rápidas
Estos datos representan un escenario realista de distribución de ayuda
"""

# Ejemplo 1: Escenario Básico (Para comenzar)
EJEMPLO_BASICO = {
    'centros': {
        'La Paz': 500,
        'Santa Cruz': 700,
        'Cochabamba': 400
    },
    'demandas': {
        'Beni': 300,
        'Rurrenabaque': 400,
        'Tipuani': 250,
        'Cobija': 350
    },
    'costos': [
        [8, 5, 4, 9],      # La Paz
        [6, 7, 8, 5],      # Santa Cruz
        [5, 4, 6, 8]       # Cochabamba
    ]
}

# Ejemplo 2: Escenario Intermedio (Para validar)
EJEMPLO_INTERMEDIO = {
    'centros': {
        'Central La Paz': 1000,
        'Centro Occidente': 800,
        'Centro Oriente': 1200,
        'Centro Norte': 600
    },
    'demandas': {
        'Altiplano': 600,
        'Valles': 800,
        'Yungas': 500,
        'Beni': 400,
        'Oruro': 300
    },
    'costos': [
        [2, 4, 6, 8, 5],           # Central La Paz
        [3, 2, 4, 7, 4],           # Centro Occidente
        [5, 6, 8, 2, 3],           # Centro Oriente
        [7, 5, 3, 4, 2]            # Centro Norte
    ]
}

# Ejemplo 3: Escenario Complejo (Para demostración avanzada)
EJEMPLO_COMPLEJO = {
    'centros': {
        'Almacén La Paz': 2000,
        'Centro Distribución Cochabamba': 1500,
        'Hub Santa Cruz': 2500,
        'Terminal Oruro': 1000,
        'Depósito Potosí': 800
    },
    'demandas': {
        'Zona Rural Altiplano': 800,
        'Zona Urbana La Paz': 1200,
        'Cochabamba Metropolitano': 600,
        'Santa Cruz Urbana': 1000,
        'Oruro y Zonas': 500,
        'Chuquisaca': 400,
        'Potosí': 300,
        'Tarija': 500
    },
    'costos': [
        [1, 2, 5, 8, 7, 6, 8, 9],
        [4, 3, 2, 5, 4, 3, 5, 6],
        [6, 7, 5, 2, 4, 7, 8, 9],
        [5, 4, 3, 6, 2, 4, 3, 5],
        [8, 7, 6, 5, 4, 2, 1, 3]
    ]
}

# Información sobre cada ejemplo
DESCRIPCIONES = {
    'BASICO': """
    ESCENARIO BÁSICO
    - 3 Centros de Acopio
    - 4 Zonas Afectadas
    - Oferta Total: 1,600 unidades
    - Demanda Total: 1,300 unidades
    - Complejidad: Baja
    
    Uso: Perfecto para entender el modelo y validar la solución
    """,
    
    'INTERMEDIO': """
    ESCENARIO INTERMEDIO
    - 4 Centros de Acopio
    - 5 Zonas Afectadas
    - Oferta Total: 3,600 unidades
    - Demanda Total: 2,600 unidades
    - Complejidad: Media
    
    Uso: Validar el sistema con casos más realistas
    """,
    
    'COMPLEJO': """
    ESCENARIO COMPLEJO
    - 5 Centros de Acopio
    - 8 Zonas Afectadas
    - Oferta Total: 7,800 unidades
    - Demanda Total: 5,300 unidades
    - Complejidad: Alta
    
    Uso: Demostración avanzada para la defensa del proyecto
    """
}


def obtener_ejemplo(tipo='basico'):
    """
    Retorna los datos de ejemplo según el tipo especificado.
    
    Args:
        tipo: 'basico', 'intermedio' o 'complejo'
    
    Returns:
        Diccionario con centros, demandas y costos
    """
    tipo = tipo.lower()
    
    if tipo == 'basico':
        return EJEMPLO_BASICO
    elif tipo == 'intermedio':
        return EJEMPLO_INTERMEDIO
    elif tipo == 'complejo':
        return EJEMPLO_COMPLEJO
    else:
        raise ValueError("Tipo debe ser 'basico', 'intermedio' o 'complejo'")


def obtener_descripcion(tipo='basico'):
    """Retorna la descripción del ejemplo"""
    tipo = tipo.upper()
    return DESCRIPCIONES.get(tipo, "Ejemplo no encontrado")


# Función auxiliar para pruebas rápidas
def cargar_ejemplo_en_sesion(session_state, tipo='basico'):
    """
    Carga un ejemplo en el state de Streamlit.
    
    Args:
        session_state: st.session_state
        tipo: Tipo de ejemplo a cargar
    """
    import numpy as np
    
    ejemplo = obtener_ejemplo(tipo)
    
    session_state.centros = ejemplo['centros']
    session_state.demandas = ejemplo['demandas']
    session_state.matriz_costos = np.array(ejemplo['costos'])
    
    return True
