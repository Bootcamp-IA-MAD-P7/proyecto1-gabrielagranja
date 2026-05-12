import time
import sqlite3
import hashlib
import unittest
from datetime import datetime

LOG_FILE = "access.log"
DEFAULT_TARIFA_PARADO = 0.02
DEFAULT_TARIFA_MOVIMIENTO = 0.05
DB_PATH = 'taximeter.db'

def taximeter():
    """
    Función para mostrar las opciones del taxímetro.
    """
    # Sistema de login/registro
    user = main_menu()
    if user is None:
        return  # Salir si el usuario cancela
    tarifa_parado, tarifa_movimiento = configurar_tarifas()
    print("=" * 40)
    print("         SISTEMA DE TAXÍMETRO")
    print("=" * 40)
    print("Bienvenido. Tarifa: "
        f"{tarifa_parado:.2f} €/s (parado) | {tarifa_movimiento:.2f} €/s (movimiento)\n")
    print("Comandos disponibles:")
    print("  'iniciar'  - Iniciar un nuevo viaje")
    print("  'detener'   - Detener el taxi (acumula tiempo parado)")
    print("  'mover'   - Reanudar movimiento (acumula tiempo en movimiento)")
    print("  'finalizar' - Finalizar el viaje y calcular tarifa")
    print("  'salir'   - Salir del programa")
    print("=" * 40 + "\n")
    
    # Declaración de variables para contar el tiempo detenido y en movimiento
    #trip_active, viaje_activo, Hay un viaje en curso
    #start_time, inicio_viaje, Cuándo empezó el viaje
    #stopped_time, tiempo_parado, Tiempo acumulado parado
    #moving_time, tiempo_movimiento, Tiempo acumulado moviéndose
    #state, estado_actual, Estado actual del taxi
    #state_start_time, inicio_estado, Cuándo empezó ese estado

    viaje_activo = False
    inicio_viaje = 0
    tiempo_parado = 0
    tiempo_movimiento = 0
    estado_actual = None # 'detenido' o 'movimiento'
    inicio_estado = 0

    # Codificando el event loop 
    should_exit = False
    while not should_exit:
        command = input("> ").strip().lower()

        if command == "iniciar":
            viaje_activo, inicio_viaje, tiempo_parado, tiempo_movimiento, estado_actual, inicio_estado = handle_iniciar(viaje_activo, inicio_viaje, tiempo_parado, tiempo_movimiento, estado_actual, inicio_estado)

        elif command in ("detener", "mover"):
            viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento = handle_detener_o_mover(command, viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento)

        elif command == "finalizar":
            viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento = handle_finalizar(viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento, tarifa_parado, tarifa_movimiento, user)

        elif command == "salir":
            should_exit = handle_salir(viaje_activo, estado_actual)

        else:
            print("Comando no reconocido. Por favor, use 'iniciar', 'detener', 'mover', 'finalizar' o 'salir'.")
            log_access_event(user, "COMMAND", False, f"Comando no reconocido: {command}")

def log_access_event(username, action, success, details=""):
    """
    Registra eventos de acceso y seguridad en un archivo de log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAIL"
    username = username if username else "UNKNOWN"
    entry = f"{timestamp} | {status} | {action} | {username} | {details}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

def calculate_fare(seconds_stopped, seconds_moving, tarifa_parado, tarifa_movimiento):
    """
    Calcula la tarifa total del viaje en función del tiempo parado
    y el tiempo en movimiento, utilizando tarifas configurables.

    Parámetros:
    - seconds_stopped: tiempo detenido en segundos.
    - seconds_moving: tiempo en movimiento en segundos.
    - tarifa_parado: precio por segundo detenido.
    - tarifa_movimiento: precio por segundo en movimiento.

    Devuelve:
    - fare: importe total del viaje en euros.
    """
    fare = (seconds_stopped * tarifa_parado + seconds_moving * tarifa_movimiento)
    return fare

def main_menu():
    """
    Menú principal para elegir entre login, registrarse como nuevo usario o salir.
    """
    init_database()  # Asegurar que la BD esté lista
    
    while True:
        print("=" * 40)
        print("    SISTEMA DE TAXÍMETRO")
        print("=" * 40)
        print("1. Iniciar sesión (Login)")
        print("2. Registrarse (Nuevo usuario)")
        print("3. Salir")
        print("=" * 40)
        
        choice = input("Seleccione una opción (1, 2 o 3): ").strip()
        
        if choice == "1":
            user = login()
            if user:
                return user
        elif choice == "2":
            user = register()
            print("Ahora puede iniciar sesión con su cuenta.\n")
        elif choice == "3":
            print("\n¡Hasta luego!\n")
            return None
        else:
            print("❌ Opción no válida. Intente de nuevo.\n")

def login():
    """
    Sistema de login con base de datos.
    """
    print("\n" + "=" * 40)
    print("         LOGIN - SISTEMA DE TAXÍMETRO")
    print("=" * 40)
    
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        username = input("Usuario: ").strip()
        password = input("Contraseña: ").strip()
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = sqlite3.connect('taximeter.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, pwd_hash))
        result = c.fetchone()
        conn.close()
        
        if result:
            print(f"\n✓ ¡Bienvenido, {username}!\n")
            log_access_event(username, "LOGIN", True, "Login exitoso")
            return username
        else:
            attempts += 1
            remaining = max_attempts - attempts
            log_access_event(username, "LOGIN", False, f"Credenciales incorrectas, intento {attempts}")
            if remaining > 0:
                print(f"❌ Credenciales incorrectas. Intentos restantes: {remaining}\n")
            else:
                print("❌ Demasiados intentos fallidos. Saliendo...\n")
                log_access_event(username, "LOGIN", False, "Bloqueo por demasiados intentos")
                return None
    
    return None

def register():
    """
    Sistema de registro de nuevos usuarios.
    """
    print("\n" + "=" * 40)
    print("    REGISTRO - SISTEMA DE TAXÍMETRO")
    print("=" * 40)
    
    while True:
        username = input("Ingrese un nombre de usuario: ").strip()
        
        # Valida que el usuario no exista
        conn = sqlite3.connect('taximeter.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            conn.close()
            print("❌ Este usuario ya existe. Intente con otro nombre.\n")
            log_access_event(username, "REGISTER", False, "Usuario ya existe")
            continue
        conn.close()
        
        if len(username) < 3:
            print("❌ El usuario debe tener al menos 3 caracteres.\n")
            log_access_event(username, "REGISTER", False, "Nombre de usuario demasiado corto")
            continue
        
        password = input("Ingrese una contraseña: ").strip()
        password_confirm = input("Confirme la contraseña: ").strip()
        
        if password != password_confirm:
            print("❌ Las contraseñas no coinciden.\n")
            log_access_event(username, "REGISTER", False, "Contraseñas no coinciden")
            continue
        
        if len(password) < 5:
            print("❌ La contraseña debe tener al menos 5 caracteres.\n")
            log_access_event(username, "REGISTER", False, "Contraseña demasiado corta")
            continue
        
        # Registrar el nuevo usuario
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('taximeter.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
        conn.commit()
        conn.close()
        
        print(f"\n✓ ¡Usuario '{username}' registrado exitosamente!\n")
        log_access_event(username, "REGISTER", True, "Registro exitoso")
        return username


def configurar_tarifas():
    """
    Permite configurar las tarifas del taxímetro.
    """
    print("\nConfiguración de tarifas")
    print("Pulsa Enter para usar los valores por defecto.")

    tarifa_parado = input(f"Tarifa por segundo parado [{DEFAULT_TARIFA_PARADO}]: ").strip()
    tarifa_movimiento = input(f"Tarifa por segundo en movimiento [{DEFAULT_TARIFA_MOVIMIENTO}]: ").strip()

    if tarifa_parado == "":
        tarifa_parado = DEFAULT_TARIFA_PARADO
    else:
        tarifa_parado = float(tarifa_parado)

    if tarifa_movimiento == "":
        tarifa_movimiento = DEFAULT_TARIFA_MOVIMIENTO
    else:
        tarifa_movimiento = float(tarifa_movimiento)

    return tarifa_parado, tarifa_movimiento

def init_database():
    """
    Inicializa la base de datos SQLite con tabla de usuarios.
    """
    conn = sqlite3.connect('taximeter.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
    
    # Insertar usuarios por defecto si no existen
    default_users = [
        ('gabriela', '123'),
        ('Invitado', '123'),
        ('admin', '123')
    ]
    
    for username, password in default_users:
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        try:
            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
        except sqlite3.IntegrityError:
            pass  # Usuario ya existe
    
    conn.commit()
    conn.close()

def update_state_duration(estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento):
    """
    Actualiza el tiempo acumulado basado en el estado actual.
    
    Parámetros:
    - estado_actual: estado actual ('detenido' o 'movimiento')
    - inicio_estado: tiempo de inicio del estado actual
    - tiempo_parado: tiempo acumulado parado (float)
    - tiempo_movimiento: tiempo acumulado en movimiento (float)
    
    Devuelve:
    - tiempo_parado, tiempo_movimiento: valores actualizados
    """
    duration = time.time() - inicio_estado
    if estado_actual == "detenido":
        tiempo_parado += duration
    else:
        tiempo_movimiento += duration
    return tiempo_parado, tiempo_movimiento


def create_trip_state():
    """
    Create a fresh trip state dictionary for CLI or GUI use.
    """
    return {
        "active": False,
        "start_time": 0.0,
        "stopped_time": 0.0,
        "moving_time": 0.0,
        "status": None,
        "status_start_time": 0.0,
        "finished": False,
    }

def start_trip_state(state):
    """
    Start a new trip and set the initial state to stopped.
    """
    if state["active"]:
        return False
    state.update({
        "active": True,
        "start_time": time.time(),
        "stopped_time": 0.0,
        "moving_time": 0.0,
        "status": "detenido",
        "status_start_time": time.time(),
        "finished": False,
    })
    return True

def stop_trip_state(state):
    """
    Switch the trip state to stopped and accumulate moving time.
    """
    if not state["active"] or state["status"] == "detenido":
        return False
    state["stopped_time"], state["moving_time"] = update_state_duration(
        state["status"], state["status_start_time"], state["stopped_time"], state["moving_time"]
    )
    state["status"] = "detenido"
    state["status_start_time"] = time.time()
    return True

def resume_trip_state(state):
    """
    Switch the trip state to moving and accumulate stopped time.
    """
    if not state["active"] or state["status"] == "movimiento":
        return False
    state["stopped_time"], state["moving_time"] = update_state_duration(
        state["status"], state["status_start_time"], state["stopped_time"], state["moving_time"]
    )
    state["status"] = "movimiento"
    state["status_start_time"] = time.time()
    return True

def finish_trip_state(state, tarifa_parado, tarifa_movimiento, username="GUI"):
    """
    Finalize the trip, compute fare, and save the trip to history.

    Returns a result dict with totals or None if no active trip.
    """
    if not state["active"]:
        return None
    state["stopped_time"], state["moving_time"] = update_state_duration(
        state["status"], state["status_start_time"], state["stopped_time"], state["moving_time"]
    )
    total_duration = state["stopped_time"] + state["moving_time"]
    total_fare = calculate_fare(state["stopped_time"], state["moving_time"], tarifa_parado, tarifa_movimiento)
    guardar_historial(username, total_fare, total_duration, state["stopped_time"], state["moving_time"])
    state["active"] = False
    state["status"] = "finalizado"
    state["finished"] = True
    return {
        "total_fare": total_fare,
        "total_duration": total_duration,
        "stopped_time": state["stopped_time"],
        "moving_time": state["moving_time"],
    }

def reset_trip_state(state):
    """
    Reset the trip state for a new trip.
    """
    state.update(create_trip_state())
    return state

def handle_iniciar(viaje_activo, inicio_viaje, tiempo_parado, tiempo_movimiento, estado_actual, inicio_estado):
    """
    Maneja el comando 'iniciar' para iniciar un nuevo viaje.
    """
    if viaje_activo:
        print("\n⚠️  ERROR: Ya hay un viaje en curso")
        print("   Usa 'finalizar' para finalizar antes de iniciar uno nuevo.\n")
        return viaje_activo, inicio_viaje, tiempo_parado, tiempo_movimiento, estado_actual, inicio_estado
    viaje_activo = True
    inicio_viaje = time.time()
    tiempo_parado = 0
    tiempo_movimiento = 0
    estado_actual = "detenido"
    inicio_estado = time.time()
    print("Viaje iniciado. Estado inicial: 'detenido'.")
    return viaje_activo, inicio_viaje, tiempo_parado, tiempo_movimiento, estado_actual, inicio_estado

def handle_detener_o_mover(command, viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento):
    """
    Maneja los comandos 'detener' y 'mover'.
    """
    if not viaje_activo:
        print("Error: no hay un viaje en curso. Por favor empiece un viaje.")
        return viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento
    tiempo_parado, tiempo_movimiento = update_state_duration(estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento)
    estado_actual = "detenido" if command == "detener" else "movimiento"
    inicio_estado = time.time()
    print(f"Estado cambiado a '{estado_actual}'.")
    return viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento

def handle_finalizar(viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento, tarifa_parado, tarifa_movimiento, user):
    """
    Maneja el comando 'finalizar' para finalizar el viaje.
    """
    if not viaje_activo:
        print("Error: no hay un viaje en curso para finalizar.")
        return viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento
    tiempo_parado, tiempo_movimiento = update_state_duration(estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento)
    total_fare = calculate_fare(tiempo_parado, tiempo_movimiento, tarifa_parado, tarifa_movimiento)
    total_duration = tiempo_parado + tiempo_movimiento
    guardar_historial(user, total_fare, total_duration, tiempo_parado, tiempo_movimiento)
    hourly_rate = (total_fare / total_duration) * 3600 if total_duration > 0 else 0
    print("\n" + "=" * 40)
    print("       RESUMEN DE TU VIAJE")
    print("=" * 40)
    print(f"Duración total:      {total_duration:.1f} s ({total_duration/60:.1f} min)")
    print(f"Tiempo parado:       {tiempo_parado:.1f} s ({tiempo_parado/60:.1f} min)")
    print(f"Tiempo en movimiento: {tiempo_movimiento:.1f} s ({tiempo_movimiento/60:.1f} min)")
    print("-" * 40)
    print(f"Tarifa total:        € {total_fare:.2f}")
    print(f"Tarifa por hora:     € {hourly_rate:.2f}/h")
    print("=" * 40 + "\n")
    print("=" * 40)
    print("¿Qué deseas hacer ahora?")
    print("  'iniciar' - Iniciar un nuevo viaje")
    print("  'salir'  - Salir del programa")
    print("=" * 40 + "\n")
    # Reset variables para el próximo viaje
    viaje_activo = False
    estado_actual = None
    return viaje_activo, estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento

def handle_salir(viaje_activo, estado_actual):
    """
    Maneja el comando 'salir' para salir del programa.
    Devuelve True si debe salir, False si continuar.
    """
    confirm = input("¿Estás seguro de que deseas salir? (s/n): ").strip().lower()
    if confirm == "s":
        print("\n¡Gracias por usar el taxímetro! ¡Hasta luego!\n")
        log_access_event("UNKNOWN", "PROGRAM_EXIT", True, "Salida del programa")
        return True
    else:
        print("\n" + "=" * 40)
        print("Operación cancelada. Continuando...")
        print("=" * 40)
        if viaje_activo:
            print("Estado actual: Viaje en curso")
        else:
            print("Estado actual: Sin viaje activo")
        print("Próximos pasos:")
        if viaje_activo:
            print("  • 'detener'   - Detener el taxi")
            print("  • 'mover'   - Reanudar movimiento")
            print("  • 'finalizar' - Finalizar el viaje actual")
        else:
            print("  • 'iniciar'  - Iniciar un nuevo viaje")
        print("  • 'salir'   - Salir del programa")
        print("=" * 40 + "\n")
        log_access_event("UNKNOWN", "PROGRAM_EXIT", False, "Salida cancelada")
        return False


def guardar_historial(username, fare, total_duration, tiempo_parado, tiempo_movimiento):
    """
    Guarda el historial de viajes en un archivo de texto plano.
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    #Creamos la línea con formato: Fecha | Usuario | Tarifa | Duración | Parado | Moviendo
    
    registro = (
        f"{fecha} - "
        f"Usuario: {username}, "
        f"Tarifa: €{fare:.2f}, "
        f"Duración Total: {total_duration:.1f}s, "
        f"Parado: {tiempo_parado:.1f}s, "
        f"Moviendo: {tiempo_movimiento:.1f}s\n"
    )
    # "a" abre el archivo para añadir texto sin borar lo anterior.
    
    with open("historial_viajes.txt", "a", encoding="utf-8") as f:
        f.write(registro)
    print("-> Registro guardado en el archivo plano.")
    return registro

#Test Unitario para la función de guardar historial

class TestFareCalculation(unittest.TestCase):
     def test_fare_calculation(self):
        self.assertAlmostEqual(calculate_fare(0, 0, 0.02, 0.05), 0.00)
        self.assertAlmostEqual(calculate_fare(60, 0, 0.02, 0.05), 1.20)  # 60s stopped
        self.assertAlmostEqual(calculate_fare(0, 60, 0.02, 0.05), 3.00)  # 60s moving
        self.assertAlmostEqual(calculate_fare(30, 30, 0.02, 0.05), 2.10) # 30s stopped + 30s moving
        self.assertAlmostEqual(calculate_fare(120, 240, 0.02, 0.05), 14.40) # 120s stopped + 240s moving    
#MAIN
if __name__ == "__main__":
    taximeter()