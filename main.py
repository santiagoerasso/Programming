"""
Módulo principal del sistema de gestión de cine.

Este programa inicializa los datos necesarios (clientes, películas y
sesiones), y ejecuta la interfaz principal de usuario en consola
para la gestión de funciones, clientes y boletos de cine.

Autores:
    - Eder Santiago Eraso Ortega (22501966)
    - Javier Esteban Bedoya Ruiz (22501361)
    - Ana Sofia Ledesma Garcia (22501352)
    - Johan David Vivas Esquivel (22501603)
"""

from sistema_cine import SistemaCine
from models import Cliente, Pelicula, SistemaSesiones
from interfaz_cli import mostrar_menu_principal


# ===============================================================
# CARGA DE DATOS INICIALES
# ===============================================================

# Se cargan los datos iniciales de clientes, películas y sesiones
# desde los módulos correspondientes. Esto garantiza que el sistema
# tenga información disponible antes de iniciar la ejecución principal.
Cliente.cargar_clientes()
Pelicula.cargar_cartelera()
SistemaSesiones.cargar_sesiones()


# ===============================================================
# FUNCIÓN PRINCIPAL
# ===============================================================

def main():
    """
    Ejecuta el flujo principal del sistema de gestión de cine.

    Esta función inicializa el objeto principal del sistema y muestra
    el menú de interacción en consola, desde donde se pueden gestionar
    películas, clientes y sesiones.
    """
    print("\n🎬 BIENVENID@ AL SISTEMA DE GESTIÓN DE CINE 🎬")
    print("==============================================")

    sistema = SistemaCine()
    mostrar_menu_principal(sistema)


# ===============================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ===============================================================

if __name__ == "__main__":
    main()
