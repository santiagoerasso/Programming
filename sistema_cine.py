# Eder Santiago Eraso Ortega (22501966)
# Javier Esteban Bedoya Ruiz (22501361)
# Ana Sofia Ledesma Garcia (2251352)
# Johan David Vivas Esquivel (22501603)

import pickle
import os
from models import Sala2D, Sala3D, SistemaSesiones, PRECIOS, Cliente

import pickle
import os

class SistemaCine:
    ARCHIVO_VENTAS = "ventas.pkl"

    def __init__(self):
        self.ventas = self.cargar_ventas()
        self.sesiones = SistemaSesiones.cargar_sesiones()
        if not self.sesiones:
            print("⚙️ No se encontraron sesiones. Generando sesiones por defecto...")
            self.sesiones = SistemaSesiones.inicializar_sesiones_por_defecto()

    # ==================================================
    # REGISTRO DE COMPRAS
    # ==================================================
    def registrar_compra(self, cliente, sesion, sillas, combos, total):
        """Registra una compra completa en el sistema."""
        venta = {
            "pelicula": sesion.pelicula.nombre,
            "sala": sesion.sala._tipo,
            "horario": sesion.horario,
            "sillas": sillas,  # lista de coordenadas de sillas
            "combos": [],      # lista de dicts con {nombre, cantidad}
            "total": total,
            "cliente_id": cliente.id_cliente
        }

        # Convertir combos de strings ("2x Combo Familiar") a dict
        for c in combos:
            partes = c.lower().split("x", 1)
            if len(partes) == 2:
                cantidad = int(partes[0].strip())
                nombre_combo = partes[1].strip().title()
                venta["combos"].append({"nombre": nombre_combo, "cantidad": cantidad})

        self.ventas.append(venta)
        self.guardar_ventas()


    # ==================================================
    # PERSISTENCIA CON PICKLE
    # ==================================================
    def guardar_ventas(self):
        with open(self.ARCHIVO_VENTAS, "wb") as f:
            pickle.dump(self.ventas, f)

    def cargar_ventas(self):
        if os.path.exists(self.ARCHIVO_VENTAS):
            with open(self.ARCHIVO_VENTAS, "rb") as f:
                return pickle.load(f)
        return []

    # ==================================================
    # ESTADÍSTICAS
    # ==================================================
# ==================================================
# ESTADÍSTICAS
# ==================================================
    def generar_estadisticas(self):
        total_boletos = 0
        total_combos = 0
        total_ventas = 0
        peliculas_vendidas = {}
        sala_ocupacion = {}  # <-- Nuevo diccionario para contar ocupación por sala

        for v in self.ventas:
            peli = v.get("pelicula", "Desconocida")
            sillas = v.get("sillas", [])
            combos = v.get("combos", [])
            sala = v.get("sala", "Desconocida")  # <-- Tomamos la sala
            total = v.get("total", 0)

            # 🎬 Asegurar que la película sea texto
            if isinstance(peli, dict):
                titulo = peli.get("titulo", "Desconocida")
            else:
                titulo = str(peli)

            # 📊 Contar boletos
            total_boletos += len(sillas)
            peliculas_vendidas[titulo] = peliculas_vendidas.get(titulo, 0) + len(sillas)

            # 📊 Contar ocupación por sala
            sala_ocupacion[sala] = sala_ocupacion.get(sala, 0) + len(sillas)

            # 🍿 Contar combos
            for combo in combos:
                if isinstance(combo, dict):
                    total_combos += combo.get("cantidad", 0)
                elif isinstance(combo, tuple) and len(combo) >= 2:
                    total_combos += combo[1]  # si combos guardan (nombre, cantidad)

            # 💰 Sumar total
            total_ventas += total

        return {
            "boletos_vendidos": total_boletos,
            "combos_vendidos": total_combos,
            "total_recaudado": total_ventas,
            "peliculas_vendidas": peliculas_vendidas,
            "sala_ocupacion": sala_ocupacion  # <-- Incluimos las salas
        }


    def generar_reporte_ventas(self):
        """Genera y muestra el reporte de ventas en consola."""
        stats = self.generar_estadisticas()

        print("\n📈 REPORTE DE ESTADÍSTICAS")
        print("────────────────────────────")
        print(f"🎟️ Total boletos vendidos: {stats['boletos_vendidos']}")
        print(f"🍿 Total combos vendidos: {stats['combos_vendidos']}")
        print(f"💰 Ingresos totales: ${stats['total_recaudado']:,} COP")

        # Obtener película más vendida
        if stats["peliculas_vendidas"]:
            pelicula_top = max(stats["peliculas_vendidas"], key=stats["peliculas_vendidas"].get)
        else:
            pelicula_top = "N/A"
        print(f"🏆 Película más vendida: {pelicula_top}")

        # Obtener sala con mayor ocupación
        if stats.get("sala_ocupacion"):
            sala_top = max(stats["sala_ocupacion"], key=stats["sala_ocupacion"].get)
        else:
            sala_top = "N/A"
        print(f"🏛️ Sala con mayor ocupación: {sala_top}")



    def obtener_salas(self):
        """Devuelve la lista de salas disponibles del sistema."""
        if not hasattr(self, "sesiones") or not self.sesiones:
            print("⚠️ Error: No hay sesiones cargadas en el sistema.")
            return []

        return [sesion.sala for sesion in self.sesiones]