# Eder Santiago Eraso Ortega (22501966)
# Javier Esteban Bedoya Ruiz (22501361)
# Ana Sofia Ledesma Garcia (2251352)
# Johan David Vivas Esquivel (22501603)

from colorama import Fore, Style
import pickle
import os
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

# Configuración de precios centralizada
PRECIOS = {
    "2D_general": 10000,
    "2D_preferencial": 12000,
    "3D_general": 15000,
    "3D_preferencial": 20000,
    "combo_individual": 10000,
    "combo_pareja": 18000,
    "combo_familiar": 30000
}

# ==========================
# CLASE SILLA
# ==========================
class Silla:
    def __init__(self, coordenada, tipo="general"):
        self._coordenada = coordenada
        self._estado = "disponible"  # disponible | ocupada | reservada
        self._tipo = tipo  # general | preferencial

    def to_dict(self):
        return {
            'coordenada': self._coordenada,
            'estado': self._estado,
            'tipo': self._tipo
        }

    @classmethod
    def from_dict(cls, data):
        required_keys = ['coordenada', 'estado', 'tipo']
        if not all(key in data for key in required_keys):
            raise ValueError("Datos de silla incompletos.")
        silla = cls(data['coordenada'], data['tipo'])
        silla._estado = data['estado']
        return silla

# ==========================
# CLASE SALA
# ==========================
class Sala(ABC):
    def __init__(self, id_sala, tipo, filas, columnas):
        self._id_sala = id_sala
        self._tipo = tipo
        self._filas = filas
        self._columnas = columnas
        self._sillas = self._generar_sillas(filas, columnas)
        self._precio_general = PRECIOS.get(f"{tipo}_general", 0)

    @abstractmethod
    def _generar_sillas(self, filas, columnas):
        pass

    def mostrar_mapa_sillas(self):
        print(f"\n🎬 Mapa de Sala {self._tipo} (ID: {self._id_sala})\n")

        for i, fila in enumerate(self._sillas):
            fila_str = ""
            for silla in fila:
                if silla._estado == "ocupada":
                    fila_str += "🟥 "
                elif silla._estado == "reservada":
                    fila_str += "🟨 "
                elif silla._tipo == "preferencial":
                    fila_str += "⭐ "
                else:
                    fila_str += "🟩 "
            print(chr(65 + i), fila_str)

        print("  " + " ".join([f"{j+1:2}" for j in range(len(self._sillas[0]))]))
        print("\n🟩 Disponible   🟨 Reservada   🟥 Ocupada   ⭐ Preferencial\n")

    def buscar_silla_por_coordenada(self, coord):
        try:
            fila_letra = coord[0].upper()
            num_col = int(coord[1:]) - 1
            fila_idx = ord(fila_letra) - 65
            if 0 <= fila_idx < self._filas and 0 <= num_col < self._columnas:
                return self._sillas[fila_idx][num_col]
            return None
        except (IndexError, ValueError):
            return None

    def precio_por_silla(self, tipo="general"):
        return PRECIOS.get(f"{self._tipo}_{tipo}", self._precio_general)

    def to_dict(self):
        return {
            'id_sala': self._id_sala,
            'tipo': self._tipo,
            'filas': self._filas,
            'columnas': self._columnas,
            'sillas': [[s.to_dict() for s in fila] for fila in self._sillas]
        }

    @classmethod
    def from_dict(cls, data):
        if data['tipo'] == '2D':
            sala = Sala2D(data['id_sala'], data['filas'], data['columnas'])
        elif data['tipo'] == '3D':
            sala = Sala3D(data['id_sala'], data['filas'], data['columnas'])
        else:
            raise ValueError("Tipo de sala inválido.")
        # Restaurar estado de sillas si vienen en el dict
        if 'sillas' in data:
            sala._sillas = [[Silla.from_dict(s) for s in fila] for fila in data['sillas']]
        return sala

class Sala2D(Sala):
    def __init__(self, id_sala, filas=10, columnas=15):
        super().__init__(id_sala, "2D", filas, columnas)

    def _generar_sillas(self, filas, columnas):
        sillas = []
        inicio_pref = max(0, filas // 2 - 1)
        fin_pref = min(filas - 1, filas // 2 + 1)
        for i in range(filas):
            fila = []
            for j in range(columnas):
                coord = f"{chr(65 + i)}{j + 1}"
                tipo = "preferencial" if inicio_pref <= i <= fin_pref else "general"
                fila.append(Silla(coord, tipo))
            sillas.append(fila)
        return sillas

class Sala3D(Sala):
    def __init__(self, id_sala, filas=10, columnas=20):
        super().__init__(id_sala, "3D", filas, columnas)

    def _generar_sillas(self, filas, columnas):
        sillas = []
        inicio_pref = max(0, filas // 2 - 1)
        fin_pref = min(filas - 1, filas // 2 + 1)
        for i in range(filas):
            fila = []
            for j in range(columnas):
                coord = f"{chr(65 + i)}{j + 1}"
                tipo = "preferencial" if inicio_pref <= i <= fin_pref else "general"
                fila.append(Silla(coord, tipo))
            sillas.append(fila)
        return sillas

# ==========================
# CLASE SESION
# ==========================
class SistemaSesiones:
    _sesiones = []
    _archivo_sesiones = "sesiones.pkl"

    @classmethod
    def obtener_sesiones(cls):
        """Devuelve todas las sesiones."""
        return cls._sesiones

    @classmethod
    def agregar_sesion(cls, sesion):
        """Agrega una sesión y guarda."""
        cls._sesiones.append(sesion)
        cls.guardar_sesiones()

    @classmethod
    def guardar_sesiones(cls):
        """Guarda las sesiones en un archivo pickle."""
        with open(cls._archivo_sesiones, "wb") as f:
            pickle.dump([s.to_dict() for s in cls._sesiones], f)

    @classmethod
    def cargar_sesiones(cls):
        """Carga las sesiones desde un archivo pickle."""
        if os.path.exists(cls._archivo_sesiones):
            with open(cls._archivo_sesiones, "rb") as f:
                data = pickle.load(f)
                cls._sesiones = [Sesion.from_dict(d) for d in data]
        return cls._sesiones
    
    @classmethod
    def inicializar_sesiones_por_defecto(cls):
        """Inicializa sesiones por defecto, corrige duplicados y convierte formatos antiguos."""
        from models import Pelicula, Sala2D, Sala3D, Sesion

        sesiones_limpias = []

        # 1️⃣ Intentar cargar sesiones previas (si existen)
        if os.path.exists(cls._archivo_sesiones):
            try:
                with open(cls._archivo_sesiones, "rb") as f:
                    data = pickle.load(f)

                # Si son dicts → convertirlos
                if data and isinstance(data[0], dict):
                    print("♻️ Convirtiendo sesiones antiguas (formato dict) a objetos Sesion...")
                    sesiones_limpias = [Sesion.from_dict(d) for d in data]

                # Si ya son objetos Sesion
                elif data and isinstance(data[0], Sesion):
                    sesiones_limpias = data

            except Exception as e:
                print(f"⚠️ Error al cargar sesiones previas ({e}), se regenerarán.")

        # 2️⃣ Crear sesiones por defecto si no hay válidas
        if not sesiones_limpias:
            print("⚙️ Generando sesiones por defecto...")
            peliculas = Pelicula.cargar_cartelera()
            sala_2d = Sala2D(1)
            sala_3d = Sala3D(2)

            for peli in peliculas:
                for horario in peli.horarios:
                    sala = sala_3d if "Avatar" in peli.nombre or "Spider" in peli.nombre else sala_2d
                    sesiones_limpias.append(Sesion(peli, horario, sala))

        # 3️⃣ 🔍 Eliminar duplicados (por película, horario y tipo de sala)
        sesiones_unicas = []
        vistos = set()

        for s in sesiones_limpias:
            key = (getattr(s.pelicula, "nombre", str(s.pelicula)), s.horario, getattr(s.sala, "tipo", str(s.sala)))
            if key not in vistos:
                sesiones_unicas.append(s)
                vistos.add(key)

        # 4️⃣ Guardar sesiones corregidas
        cls._sesiones = sesiones_unicas
        cls.guardar_sesiones()
        print(f"✅ {len(sesiones_unicas)} sesiones cargadas correctamente (duplicados eliminados).")

        return cls._sesiones



class Sesion:
    def __init__(self, pelicula, horario, sala):
        self.pelicula = pelicula
        self.horario = horario
        self.sala = sala
        # Cada sesión mantiene su propio estado de sillas (copia de la plantilla de la sala)
        self._sillas_estado = [[Silla(s._coordenada, s._tipo) for s in fila] for fila in sala._sillas]

    # Mostrar mapa (CLI espera mostrar_mapa_sillas)
    def mostrar_mapa_sillas(self):
        print(f"\n🎬 Mapa de Sesión: {self.pelicula.nombre} - {self.horario} (Sala {self.sala._tipo})\n")
        for i, fila in enumerate(self._sillas_estado):
            fila_str = ""
            for silla in fila:
                if silla._estado == "ocupada":
                    fila_str += "🟥 "
                elif silla._estado == "reservada":
                    fila_str += "🟨 "
                elif silla._tipo == "preferencial":
                    fila_str += "⭐ "
                else:
                    fila_str += "🟩 "
            print(chr(65 + i), fila_str)
        # encabezado de columnas
        print("  " + " ".join([f"{j+1:2}" for j in range(len(self._sillas_estado[0]))]))
        print("\n🟩 Disponible   🟨 Reservada   🟥 Ocupada   ⭐ Preferencial\n")

    # Compatibilidad: si el frontend llama a mostrar_sala()
    def mostrar_sala(self):
        # alias a mostrar_mapa_sillas para compatibilidad
        self.mostrar_mapa_sillas()

    # Mostrar combos (frontend llama a sesion.mostrar_combos())
    def mostrar_combos(self):
        print("\n🍿 COMBOS DISPONIBLES:")
        print(f"1. Combo Individual - ${PRECIOS['combo_individual']:,} COP")
        print(f"2. Combo Pareja - ${PRECIOS['combo_pareja']:,} COP")
        print(f"3. Combo Familiar - ${PRECIOS['combo_familiar']:,} COP")
        print("0. No agregar combos")

    def buscar_silla_por_coordenada(self, coord):
        try:
            fila_letra = coord[0].upper()
            num_col = int(coord[1:]) - 1
            fila_idx = ord(fila_letra) - 65
            if 0 <= fila_idx < self.sala._filas and 0 <= num_col < self.sala._columnas:
                return self._sillas_estado[fila_idx][num_col]
            return None
        except (IndexError, ValueError):
            return None

    def liberar_silla(self, coord):
        """Libera una silla por coordenada dentro de la sesión.
           Retorna True si la liberó, False si no existe o ya estaba disponible."""
        try:
            fila_letra = coord[0].upper()
            num_col = int(coord[1:]) - 1
            fila_idx = ord(fila_letra) - 65
            if not (0 <= fila_idx < self.sala._filas and 0 <= num_col < self.sala._columnas):
                return False
            silla = self._sillas_estado[fila_idx][num_col]
            if silla._estado != "disponible":
                silla._estado = "disponible"
                return True
            return False
        except Exception:
            return False

    def ocupar_silla(self, coord):
        """Marca como ocupada la silla en la sesión si está disponible."""
        try:
            fila_letra = coord[0].upper()
            num_col = int(coord[1:]) - 1
            fila_idx = ord(fila_letra) - 65
            if not (0 <= fila_idx < self.sala._filas and 0 <= num_col < self.sala._columnas):
                return False
            silla = self._sillas_estado[fila_idx][num_col]
            if silla._estado == "disponible":
                silla._estado = "ocupada"
                return True
            return False
        except Exception:
            return False

    def calcular_total(self, sillas_coords, combos_list=None, cliente=None):
        """
        Calcula el total de una compra: suma precios de sillas + combos y aplica descuentos si el cliente tiene tarjeta.
        - sillas_coords: lista de coordenadas, ej. ["G2","G3"]
        - combos_list: lista de strings con formato "Nx Nombre Combo", ej. ["2x Combo Familiar"]
        - cliente: objeto Cliente (opcional) para aplicar descuento
        Devuelve el total final (float).
        """
        # 1) Total por boletos
        total_boletos = 0
        for coord in sillas_coords or []:
            s = self.buscar_silla_por_coordenada(coord)
            if not s:
                continue
            # precio según tipo de sala y silla (ej: "2D_preferencial")
            precio = PRECIOS.get(f"{self.sala._tipo}_{s._tipo}", PRECIOS.get(f"{self.sala._tipo}_general", 0))
            total_boletos += precio

        # 2) Total por combos (parse robusto)
        total_combos = 0
        if combos_list:
            for combo_text in combos_list:
                try:
                    # Soporta formatos: "8x Combo Familiar" o "8 x Combo Familiar"
                    partes = combo_text.strip().split("x", 1)
                    if len(partes) != 2:
                        continue
                    cantidad = int(partes[0].strip())
                    nombre_combo = partes[1].strip().lower()

                    # Normalizar: quitar prefijo "combo " si existe -> buscamos claves 'combo_familiar', etc.
                    if nombre_combo.startswith("combo "):
                        nombre_combo = nombre_combo.replace("combo ", "", 1).strip()

                    key = f"combo_{nombre_combo.replace(' ', '_')}"
                    precio_combo = PRECIOS.get(key, 0)
                    total_combos += cantidad * precio_combo
                except Exception:
                    # en caso de formato inesperado, ignoramos ese combo
                    continue

        subtotal = total_boletos + total_combos

        # 3) Aplicar descuento de tarjeta (si corresponde)
        if cliente and hasattr(cliente, "calcular_descuento"):
            total_final, ahorro = cliente.calcular_descuento(subtotal)
            return total_final

        return subtotal


    def to_dict(self):
        return {
            'pelicula': self.pelicula.to_dict(),
            'horario': self.horario,
            'sala': self.sala.to_dict(),
            'sillas_estado': [[s.to_dict() for s in fila] for fila in self._sillas_estado]
        }

    @classmethod
    def from_dict(cls, data):
        required_keys = ['pelicula', 'horario', 'sala', 'sillas_estado']
        if not all(key in data for key in required_keys):
            raise ValueError("Datos de sesión incompletos.")
        pelicula = Pelicula.from_dict(data['pelicula'])
        sala = Sala.from_dict(data['sala'])
        sesion = cls(pelicula, data['horario'], sala)
        # restaurar estado de sillas en la sesión
        sesion._sillas_estado = [[Silla.from_dict(s) for s in fila] for fila in data['sillas_estado']]
        return sesion

# ==========================
# CLASE TARJETA FIDELIZACION
# ==========================
class TarjetaFidelizacion:
    def __init__(self, nombre):
        self.nombre = nombre
        self.compras_realizadas = 0
        self.nivel_actual = self.obtener_nivel()

    def registrar_compra(self):
        self.compras_realizadas += 1
        nuevo_nivel = self.obtener_nivel()
        if nuevo_nivel != self.nivel_actual:
            print(f"\n🎉 ¡Felicidades, {self.nombre}! Has subido al nivel {nuevo_nivel.upper()} 🏅")
            self.nivel_actual = nuevo_nivel
        else:
            print(f"🧾 Compra registrada. Total de compras: {self.compras_realizadas} (Nivel actual: {self.nivel_actual})")

    def obtener_nivel(self):
        if self.compras_realizadas <= 3:
            return "Clásica"
        elif self.compras_realizadas <= 6:
            return "Premium"
        else:
            return "Élite"

    def calcular_descuento(self, total):
        nivel = self.obtener_nivel()
        if nivel == "Clásica":
            descuento = 0.05
        elif nivel == "Premium":
            descuento = 0.10
        else:
            descuento = 0.15
        ahorro = total * descuento
        total_final = total - ahorro
        return total_final, ahorro

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'compras_realizadas': self.compras_realizadas,
            'nivel_actual': self.nivel_actual
        }

    @classmethod
    def from_dict(cls, data):
        tarjeta = cls(data['nombre'])
        tarjeta.compras_realizadas = data['compras_realizadas']
        tarjeta.nivel_actual = data['nivel_actual']
        return tarjeta

    def __str__(self):
        return f"{self.nivel_actual} ({self.compras_realizadas} compras)"

# ==========================
# CLASE CLIENTE
# ==========================
class Cliente:
    _clientes_registrados = []
    _archivo_clientes = "clientes.pkl"

    def __init__(self, nombre, id_cliente, telefono, tiene_tarjeta=False):
        self.nombre = nombre
        self.id_cliente = id_cliente
        self.telefono = telefono
        self.tiene_tarjeta = tiene_tarjeta
        self.tarjeta = TarjetaFidelizacion(nombre) if tiene_tarjeta else None
        self.compras = 0

    def __str__(self):
        tarjeta_info = f"Tarjeta: {self.tarjeta.nivel_actual} ✅" if self.tarjeta else "Sin tarjeta ❌"
        return f"👤 {self.nombre} | ID: {self.id_cliente} | Tel: {self.telefono} | {tarjeta_info}"

    def activar_tarjeta(self):
        if not self.tarjeta:
            self.tarjeta = TarjetaFidelizacion(self.nombre)
            self.tiene_tarjeta = True
        print(f"✅ Tarjeta activada. Nivel actual: {self.tarjeta.nivel_actual}")

    def registrar_compra(self):
        self.compras += 1
        if self.tarjeta:
            self.tarjeta.registrar_compra()

    def calcular_descuento(self, total):
        if self.tarjeta:
            return self.tarjeta.calcular_descuento(total)
        return total, 0

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'id_cliente': self.id_cliente,
            'telefono': self.telefono,
            'tiene_tarjeta': self.tiene_tarjeta,
            'tarjeta': self.tarjeta.to_dict() if self.tarjeta else None,
            'compras': self.compras
        }

    @classmethod
    def from_dict(cls, data):
        cliente = cls(data['nombre'], data['id_cliente'], data['telefono'], data['tiene_tarjeta'])
        if data.get('tarjeta'):
            cliente.tarjeta = TarjetaFidelizacion.from_dict(data['tarjeta'])
        cliente.compras = data.get('compras', 0)
        return cliente

    @classmethod
    def guardar_clientes(cls):
        """Guarda la lista completa de clientes."""
        with open(cls._archivo_clientes, "wb") as f:
            pickle.dump([c.to_dict() for c in cls._clientes_registrados], f)

    @classmethod
    def cargar_clientes(cls):
        """Carga los clientes del archivo pickle."""
        if os.path.exists(cls._archivo_clientes):
            with open(cls._archivo_clientes, "rb") as f:
                data = pickle.load(f)
                cls._clientes_registrados = [cls.from_dict(d) for d in data]
        return cls._clientes_registrados

    @classmethod
    def registrar_cliente(cls, cliente):
        """Agrega un cliente si no existe y guarda."""
        cls.cargar_clientes()
        if any(c.id_cliente == cliente.id_cliente for c in cls._clientes_registrados):
            print(f"⚠️ Ya existe un cliente con ID {cliente.id_cliente}.")
            return False
        cls._clientes_registrados.append(cliente)
        cls.guardar_clientes()
        return True

    @classmethod
    def buscar_cliente_por_id(cls, id_cliente):
        """Busca cliente por ID."""
        cls.cargar_clientes()
        for c in cls._clientes_registrados:
            if c.id_cliente == id_cliente:
                return c
        return None

    @classmethod
    def eliminar_cliente(cls, id_cliente):
        """Elimina cliente y guarda el cambio."""
        cls.cargar_clientes()
        for c in cls._clientes_registrados:
            if c.id_cliente == id_cliente:
                cls._clientes_registrados.remove(c)
                cls.guardar_clientes()
                print(f"✅ Cliente con ID {id_cliente} eliminado correctamente.")
                return
        print(f"❌ No se encontró ningún cliente con ID {id_cliente}.")

    @classmethod
    def ver_clientes(cls):
        """Muestra todos los clientes."""
        cls.cargar_clientes()
        if not cls._clientes_registrados:
            print("📭 No hay clientes registrados.")
            return
        print("\n📋 CLIENTES REGISTRADOS:")
        for c in cls._clientes_registrados:
            print("-", c)

    @classmethod
    def buscar_por_nombre(cls, nombre):
        cls.cargar_clientes()
        encontrados = [c for c in cls._clientes_registrados if nombre.lower() in c.nombre.lower()]
        if encontrados:
            print(f"\n✅ {len(encontrados)} cliente(s) encontrado(s):")
            for c in encontrados:
                print("-", c)
        else:
            print("❌ No se encontró ningún cliente con ese nombre.")

    @classmethod
    def buscar_por_telefono(cls, telefono):
        cls.cargar_clientes()
        encontrados = [c for c in cls._clientes_registrados if c.telefono == telefono]
        if encontrados:
            print("\n✅ Cliente(s) encontrado(s):")
            for c in encontrados:
                print("-", c)
        else:
            print("❌ No se encontró ningún cliente con ese teléfono.")

    @classmethod
    def buscar_por_nivel(cls, nivel):
        cls.cargar_clientes()
        nivel_map = {"c": "Clásica", "p": "Premium", "e": "Élite"}
        if nivel.lower() not in nivel_map:
            print("❌ Nivel inválido. Use c/p/e.")
            return
        nivel_nombre = nivel_map[nivel.lower()]
        encontrados = [c for c in cls._clientes_registrados if c.tarjeta and c.tarjeta.nivel_actual == nivel_nombre]
        if encontrados:
            print(f"\n✅ Clientes con tarjeta {nivel_nombre}:")
            for c in encontrados:
                print("-", c)
        else:
            print(f"❌ No se encontraron clientes con tarjeta {nivel_nombre}.")

# ==========================
# CLASE PELICULA
# ==========================
class Pelicula:
    _cartelera = []
    _archivo_cartelera = "cartelera.pkl"

    def __init__(self, nombre, duracion, genero, clasificacion, horarios):
        self.nombre = nombre
        self.duracion = duracion
        self.genero = genero
        self.clasificacion = clasificacion
        self.horarios = horarios

    def __str__(self):
        horarios_str = ", ".join(self.horarios)
        return (
            f"{Fore.CYAN}🎬 {self.nombre}{Style.RESET_ALL}\n"
            f"   🕒 Duración: {self.duracion}\n"
            f"   🎭 Género: {self.genero}\n"
            f"   🔞 Clasificación: {self.clasificacion}\n"
            f"   ⏰ Horarios: {horarios_str}\n"
        )

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'duracion': self.duracion,
            'genero': self.genero,
            'clasificacion': self.clasificacion,
            'horarios': self.horarios
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('nombre', 'Desconocida'),
            data.get('duracion', ''),
            data.get('genero', ''),
            data.get('clasificacion', ''),
            data.get('horarios', [])
        )

    @classmethod
    def cargar_cartelera(cls):
        """Inicializa la cartelera con películas por defecto si no existen."""
        if os.path.exists(cls._archivo_cartelera):
            with open(cls._archivo_cartelera, "rb") as f:
                data = pickle.load(f)
                cls._cartelera = [cls.from_dict(d) for d in data]
        elif not cls._cartelera:
            cls._cartelera = [
                Pelicula(
                    "Avengers: Endgame",
                    "3h 2m",
                    "Acción / Ciencia Ficción",
                    "PG-13",
                    ["1:00 PM", "4:30 PM", "8:00 PM"]
                ),
                Pelicula(
                    "Toy Story 4",
                    "1h 40m",
                    "Animación / Aventura",
                    "ATP",
                    ["11:00 AM", "2:00 PM", "5:00 PM"]
                ),
                Pelicula(
                    "Avatar: El camino del agua",
                    "3h 12m",
                    "Fantasía / Aventura",
                    "PG-13",
                    ["12:00 PM", "4:00 PM", "8:30 PM"]
                ),
                Pelicula(
                    "Spider-Man: No Way Home",
                    "2h 28m",
                    "Acción / Superhéroes",
                    "PG-13",
                    ["10:30 AM", "3:00 PM", "7:30 PM"]
                ),
                Pelicula(
                    "Encanto",
                    "1h 42m",
                    "Animación / Musical",
                    "ATP",
                    ["10:00 AM", "1:00 PM", "4:00 PM"]
                ),
            ]
            cls.guardar_cartelera()
        return cls._cartelera

    @classmethod
    def guardar_cartelera(cls):
        """Guarda la cartelera en un archivo pickle.""" 
        with open(cls._archivo_cartelera, "wb") as f:
            pickle.dump([p.to_dict() for p in cls._cartelera], f)

    @classmethod
    def mostrar_cartelera(cls):
        """Muestra todas las películas disponibles."""
        peliculas = cls.cargar_cartelera()
        print("\n🍿 CARTELERA DE HOY 🍿")
        print("───────────────────────────────")
        for i, pelicula in enumerate(peliculas, start=1):
            print(f"{Fore.YELLOW}{i}. {pelicula}")

# ==========================
# CLASE COMBO
# ==========================
class Combo:
    def __init__(self, id_combo, tipo, precio):
        self._id_combo = id_combo
        self._tipo = tipo
        self._precio = precio

    def __str__(self):
        return f"Combo {self._tipo} - ${self._precio:,.0f}"

# ==========================
# CLASE ENTRADA
# ==========================
class Entrada:
    def __init__(self, id_entrada, id_compra, id_sala, coordenada, categoria, precio, horario):
        self._id_entrada = id_entrada
        self._id_compra = id_compra
        self._id_sala = id_sala
        self._coordenada = coordenada
        self._categoria = categoria
        self._precio = precio
        self._horario = horario
        self._estado = "activa"

    def cancelar(self):
        self._estado = "cancelada"

# ==========================
# CLASE COMPRA
# ==========================
class Compra:
    def __init__(self, id_compra, cliente_id, entradas, combos, total):
        self._id_compra = id_compra
        self._cliente_id = cliente_id
        self._entradas = entradas or []
        self._combos = combos or []
        self._fecha = datetime.now()
        self._total = total
        self._estado = "activa"

    def cancelar(self):
        self._estado = "cancelada"
        for e in self._entradas:
            e.cancelar()