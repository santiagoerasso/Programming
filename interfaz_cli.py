# Eder Santiago Eraso Ortega (22501966)
# Javier Esteban Bedoya Ruiz (22501361)
# Ana Sofia Ledesma Garcia (2251352)
# Johan David Vivas Esquivel (22501603)

from models import Cliente, TarjetaFidelizacion, Pelicula, Sesion, SistemaSesiones, PRECIOS, Combo, Entrada, Compra, Sala
import re
import random
from colorama import Fore, Style, init
init(autoreset=True)

# ====== FUNCIONES PRINCIPALES DE INTERFAZ CLI ======

def mostrar_menu_principal(sistema):
    while True:
        print(f"\n{Fore.CYAN}🎥 SISTEMA DE CINE 🎥{Style.RESET_ALL}")
        print("────────────────────────────")
        print("1. Entradas")
        print("2. Clientes")
        print("3. Cartelera")
        print("4. Admin")
        print("5. Guardar y Salir")
        print("0. Salir sin Guardar")
        print("────────────────────────────")

        opcion = input("Seleccione una opción: ")

        if opcion == "0":
            # Liberar todas las sillas ocupadas antes de salir sin guardar
            for sesion in SistemaSesiones.obtener_sesiones():
                for fila in sesion.sala._sillas:
                    for silla in fila:
                        if silla._estado == "ocupada":
                            silla._estado = "disponible"
            print("\n👋 ¡Gracias por visitar nuestro cine!")
            break
        elif opcion == "1":
            menu_entradas(sistema)
        elif opcion == "2":
            menu_clientes()
        elif opcion == "3":
            Pelicula.mostrar_cartelera()
        elif opcion == "4":
            menu_admin(sistema)
        elif opcion == "5":
            Pelicula.guardar_cartelera()
            Cliente.guardar_clientes()
            SistemaSesiones.guardar_sesiones()
            sistema.guardar_ventas()
            print("\n💾 Datos guardados. ¡Gracias por visitar nuestro cine!")
            break
        else:
            print("❌ Opción inválida. Intente nuevamente.")

def menu_entradas(sistema):
    print("\n🎞️  SECCIÓN DE ENTRADAS 🎞️")
    print("────────────────────────────")
    
    # 1️⃣ Mostrar cartelera
    peliculas = Pelicula.cargar_cartelera()
    for i, pelicula in enumerate(peliculas, start=1):
        print(f"{i}. {pelicula.nombre}")
    
    try:
        opcion_peli = int(input("\nSeleccione la película (número): "))
        pelicula = peliculas[opcion_peli - 1]
    except (ValueError, IndexError):
        print("❌ Opción inválida. Regresando al menú principal.")
        return
    
    # 2️⃣ Mostrar horarios de la película seleccionada
    print(f"\nHas seleccionado: {Fore.YELLOW}{pelicula.nombre}{Style.RESET_ALL}")
    print("Horarios disponibles:")
    for i, horario in enumerate(pelicula.horarios, start=1):
        print(f"{i}. {horario}")
    
    try:
        opcion_hora = int(input("\nSeleccione el horario (número): "))
        horario = pelicula.horarios[opcion_hora - 1]
    except (ValueError, IndexError):
        print("❌ Horario inválido.")
        return
    
    # 3️⃣ Buscar sesión existente o crear nueva
    from models import SistemaSesiones, Sala2D, Sala3D, Sesion

    sesiones_filtradas = [s for s in SistemaSesiones.obtener_sesiones()
                          if s.pelicula.nombre == pelicula.nombre and s.horario == horario]

    if sesiones_filtradas:
        sesion = sesiones_filtradas[0]  # ✅ Tomamos la sesión ya existente
    else:
        # Crear nueva sesión con la sala correspondiente
        sala = Sala3D(1) if "3D" in pelicula.nombre or "Avatar" in pelicula.nombre else Sala2D(1)
        sesion = Sesion(pelicula, horario, sala)
        SistemaSesiones.agregar_sesion(sesion)

    print(f"\n🎬 Película: {pelicula.nombre}")
    print(f"🕒 Horario: {horario}")
    print(f"🏛️ Sala: {sesion.sala._tipo}")
    
    # 4️⃣ Comprar boletos
    comprar_boletos(sesion, sistema)


def menu_admin(sistema):
    while True:
        print("\n🔐 MENÚ DE ADMINISTRACIÓN")
        print("────────────────────────────")
        print("1. Generar reporte de ventas")
        print("0. Volver al menú principal")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            sistema.generar_reporte_ventas()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida. Intente de nuevo.")

def menu_clientes():
    while True:
        print("\n👥 MENÚ DE CLIENTES")
        print("1. Registrar nuevo cliente")
        print("2. Ver clientes registrados")
        print("3. Buscar cliente por nombre")
        print("4. Buscar cliente por ID")
        print("5. Buscar cliente por teléfono")
        print("6. Buscar cliente por nivel de tarjeta")
        print("7. Eliminar cliente")
        print("0. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_cliente()
        elif opcion == "2":
            Cliente.ver_clientes()
        elif opcion == "3":
            nombre = input("Ingrese nombre o parte del nombre: ")
            Cliente.buscar_por_nombre(nombre)
        elif opcion == "4":
            id_cliente = input("Ingrese ID del cliente: ")
            Cliente.buscar_por_id(id_cliente)
        elif opcion == "5":
            telefono = input("Ingrese teléfono del cliente: ")
            Cliente.buscar_por_telefono(telefono)
        elif opcion == "6":
            nivel = input("Ingrese nivel (C=Clásica, P=Premium, E=Élite): ")
            Cliente.buscar_por_nivel(nivel)
        elif opcion == "7":
            id_a_eliminar = input("Ingrese el ID del cliente a eliminar: ").strip()
            confirm = input(f"¿Seguro que desea eliminar al cliente con ID {id_a_eliminar}? (s/n): ").strip().lower()
            if confirm == "s":
                Cliente.eliminar_cliente(id_a_eliminar)
            else:
                print("🚫 Eliminación cancelada.")
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida, intente de nuevo.")

def validar_coordenada(coord, sala_filas, sala_columnas):
    """Valida que una coordenada sea válida para la sala."""
    if re.match(r'^[A-J]\d{1,2}$', coord.upper()):
        fila_idx = ord(coord[0].upper()) - 65
        col = int(coord[1:]) - 1
        if 0 <= fila_idx < sala_filas and 0 <= col < sala_columnas:
            return True
    return False

def comprar_boletos(sesion, sistema):
    print("\n🎟️ COMPRA DE BOLETOS")
    print("======================")

    sillas_seleccionadas = []
    cliente = None
    compra_exitosa = False  # 🔹 indicador de éxito

    try:
        sesion.mostrar_mapa_sillas()

        while True:
            silla = input("Seleccione una silla (ejemplo: A1) o Enter para terminar: ").upper()
            if not silla:
                break

            if sesion.ocupar_silla(silla):
                sillas_seleccionadas.append(silla)
                print(f"✅ Silla {silla} ocupada temporalmente.")
            else:
                print("❌ La silla no está disponible o no existe.")

        if not sillas_seleccionadas:
            print("🚫 No se seleccionaron sillas. Cancelando compra.")
            return

        # Combos
        combos = []
        while True:
            sesion.mostrar_combos()
            opcion = input("Seleccione un combo (0-3) o Enter para continuar: ").strip()
            if not opcion or opcion == "0":
                break
            if opcion not in ("1", "2", "3"):
                print("❌ Opción inválida.")
                continue
            cantidad = input("¿Cuántos desea agregar?: ").strip()
            if not cantidad.isdigit() or int(cantidad) <= 0:
                print("❌ Cantidad inválida.")
                continue

            nombre_combo = {
                "1": "Combo Individual",
                "2": "Combo Pareja",
                "3": "Combo Familiar"
            }[opcion]

            combos.append(f"{cantidad}x {nombre_combo}")
            print(f"✅ {cantidad}x {nombre_combo} agregado(s).")

        # Buscar cliente
        print("\n👤 DATOS DEL CLIENTE")
        id_cliente = input("Ingrese su ID: ").strip()
        cliente = Cliente.buscar_cliente_por_id(id_cliente)

        if not cliente:
            print("🆕 No existe un cliente con ese ID.")
            registrar = input("¿Desea registrarse como nuevo cliente? (s/n): ").strip().lower()
            if registrar == "s":
                cliente = registrar_cliente()
                if not cliente:
                    print("🚫 No se puede continuar sin cliente registrado.")
                    return
            else:
                print("🚫 No se puede continuar sin cliente registrado.")
                return

        # Calcular total
        total = sesion.calcular_total(sillas_seleccionadas, combos, cliente)

        # Confirmar compra
        confirmar = input(f"💰 Total a pagar: ${total:,} COP. ¿Confirmar compra? (s/n): ").strip().lower()
        if confirmar != "s":
            print("❌ Compra cancelada por el usuario.")
            return

        # Registrar compra en el sistema
        sistema.registrar_compra(cliente, sesion, sillas_seleccionadas, combos, total)
        compra_exitosa = True  # 🔹 marcar éxito
        print(f"\n🎉 ¡Compra realizada exitosamente para {cliente.nombre}!")
        print(f"🎟️ Sillas: {', '.join(sillas_seleccionadas)}")
        print(f"🍿 Combos: {', '.join(combos) if combos else 'Ninguno'}")
        print(f"💵 Total pagado: ${total:,} COP")

    except Exception as e:
        print(f"⚠️ Ocurrió un error durante la compra: {e}")

    finally:
        # 🔁 Liberar sillas si la compra no fue exitosa
        if not compra_exitosa:
            for silla in sillas_seleccionadas:
                sesion.liberar_silla(silla)
            if sillas_seleccionadas:
                print("\n🔄 Las sillas seleccionadas fueron liberadas automáticamente.")


def registrar_cliente():
    print("\n🧾 REGISTRO DE NUEVO CLIENTE")
    nombre = input("Ingrese el nombre completo: ").strip().title()
    id_cliente = input("Ingrese el ID del cliente: ").strip()
    telefono = input("Ingrese el número de teléfono: ").strip()

    # Verificar si ya existe
    if Cliente.buscar_cliente_por_id(id_cliente):
        print(f"⚠️ Ya existe un cliente con el ID {id_cliente}.")
        return None  # ← devuelve None si ya existe

    # Validar tarjeta
    while True:
        tiene_tarjeta = input("¿Desea activar tarjeta de fidelización? (s/n): ").strip().lower()
        if tiene_tarjeta in ("s", "n"):
            break
        print("❌ Opción inválida. Por favor responda con 's' o 'n'.")

    nuevo_cliente = Cliente(nombre, id_cliente, telefono, tiene_tarjeta == "s")
    Cliente.registrar_cliente(nuevo_cliente)

    print("\n✅ Cliente registrado exitosamente:")
    print(nuevo_cliente)

    if nuevo_cliente.tiene_tarjeta:
        print(f"🎁 Tarjeta creada para {nuevo_cliente.nombre}. ¡Ahora eres miembro del programa de fidelización!")

    return nuevo_cliente


def reservar_sillas(sesion):
    print("\n🎟️ RESERVAR ASIENTOS")
    sesion.mostrar_mapa_sillas()

    coordenadas = input("Ingrese las coordenadas de las sillas a reservar (ej: D5,E6): ").upper().replace(" ", "").split(",")

    total = 0
    for coord in coordenadas:
        if not validar_coordenada(coord, sesion.sala._filas, sesion.sala._columnas):
            print(f"❌ Coordenada inválida: {coord}")
            continue
        silla = sesion.buscar_silla_por_coordenada(coord)
        if not silla:
            print(Fore.RED + f"Silla {coord} no existe.")
            continue
        if silla._estado == "ocupada":
            print(Fore.RED + f"Silla {coord} ya está ocupada.")
        elif silla._estado == "reservada":
            print(Fore.YELLOW + f"Silla {coord} ya está reservada.")
        else:
            silla._estado = "reservada"
            precio = PRECIOS[f"{sesion.sala._tipo}_{silla._tipo}"]
            total += precio
            if silla._tipo == "preferencial":
                print(Fore.CYAN + f"⭐ ¡Has reservado una silla preferencial {coord}! Valor: ${precio:,} COP 🎟️")
            else:
                print(Fore.CYAN + f"🎫 Silla {coord} reservada exitosamente por ${precio:,} COP.")

    if total > 0:
        print(Fore.CYAN + f"\n💰 Total de la reserva: ${total:,} COP")

    print("\nActualizando mapa...\n")
    sesion.mostrar_mapa_sillas()

def liberar_sillas(sesion):
    print("\n🔓 LIBERAR ASIENTOS")
    sesion.mostrar_mapa_sillas()

    coordenadas = input("Ingrese las coordenadas de las sillas a liberar (ej: A5,B10): ").upper().replace(" ", "").split(",")

    for coord in coordenadas:
        if not validar_coordenada(coord, sesion.sala._filas, sesion.sala._columnas):
            print(f"❌ Coordenada inválida: {coord}")
            continue
        silla = sesion.buscar_silla_por_coordenada(coord)
        if not silla:
            print(Fore.RED + f"Silla {coord} no existe.")
            continue
        if silla._estado == "disponible":
            print(Fore.YELLOW + f"Silla {coord} ya está disponible.")
        else:
            silla._estado = "disponible"
            print(Fore.GREEN + f"✅ Silla {coord} liberada correctamente.")

    print("\nActualizando mapa...\n")
    sesion.mostrar_mapa_sillas()