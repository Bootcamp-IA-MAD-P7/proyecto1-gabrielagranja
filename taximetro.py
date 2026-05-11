import time
import sqlite3
import hashlib
import unittest

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
    print(f"Total: {fare:.2f} €")
    return fare

import time
import sqlite3
import hashlib

def configurar_tarifas():
    """
    Permite configurar las tarifas del taxímetro.
    """
    print("\nConfiguración de tarifas")
    print("Pulsa Enter para usar los valores por defecto.")

    tarifa_parado = input("Tarifa por segundo parado [0.02]: ").strip()
    tarifa_movimiento = input("Tarifa por segundo en movimiento [0.05]: ").strip()

    if tarifa_parado == "":
        tarifa_parado = 0.02
    else:
        tarifa_parado = float(tarifa_parado)

    if tarifa_movimiento == "":
        tarifa_movimiento = 0.05
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



def register():
    """
    Sistema de registro de nuevos usuarios.
    """
    print("\n" + "=" * 40)
    print("    REGISTRO - SISTEMA DE TAXÍMETRO")
    print("=" * 40)
    
    while True:
        username = input("Ingrese un nombre de usuario: ").strip()
        
        # Validar que el usuario no exista
        conn = sqlite3.connect('taximeter.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        if c.fetchone():
            conn.close()
            print("❌ Este usuario ya existe. Intente con otro nombre.\n")
            continue
        conn.close()
        
        if len(username) < 3:
            print("❌ El usuario debe tener al menos 3 caracteres.\n")
            continue
        
        password = input("Ingrese una contraseña: ").strip()
        password_confirm = input("Confirme la contraseña: ").strip()
        
        if password != password_confirm:
            print("❌ Las contraseñas no coinciden.\n")
            continue
        
        if len(password) < 5:
            print("❌ La contraseña debe tener al menos 5 caracteres.\n")
            continue
        
        # Registrar el nuevo usuario
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('taximeter.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
        conn.commit()
        conn.close()
        
        print(f"\n✓ ¡Usuario '{username}' registrado exitosamente!\n")
        return username

def main_menu():
    """
    Menú principal para elegir entre login y registro.
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
            return username
        else:
            attempts += 1
            remaining = max_attempts - attempts
            if remaining > 0:
                print(f"❌ Credenciales incorrectas. Intentos restantes: {remaining}\n")
            else:
                print("❌ Demasiados intentos fallidos. Saliendo...\n")
                return None
    
    return None

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
    print("  'start'  - Iniciar un nuevo viaje")
    print("  'stop'   - Detener el taxi (acumula tiempo parado)")
    print("  'move'   - Reanudar movimiento (acumula tiempo en movimiento)")
    print("  'finish' - Finalizar el viaje y calcular tarifa")
    print("  'exit'   - Salir del programa")
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
    estado_actual = None # 'stopped' o 'moving'
    inicio_estado = 0

    # Codificando el event loop 
    
    while True:
        command = input("> ").strip().lower()

        if command == "start":
            if viaje_activo:
                print("\n⚠️  ERROR: Ya hay un viaje en curso")
                print("   Usa 'finish' para finalizar antes de iniciar uno nuevo.\n")
                continue
            viaje_activo = True
            inicio_viaje = time.time()
            tiempo_parado = 0
            tiempo_movimiento = 0
            estado_actual = "stopped"
            inicio_estado = time.time()
            print("Viaje iniciado. Estado incial: 'stopped'.")

        elif command in ("stop", "move"):
            if not viaje_activo:
                print("Error: no hay un viaje en curso. Por favor empice un viaje.")
                continue
            #calcula el tiempo transcurrido en el estado actual antes de cambiar
            duration= time.time() - inicio_estado 
            if estado_actual == "stopped":
                tiempo_parado += duration
            else:
                tiempo_movimiento += duration

            # Cambio el estado actual y reinicia el tiempo de inicio del estado
            estado_actual = "stopped" if command == "stop" else "moving"
            inicio_estado = time.time()
            print(f"state changed to '{estado_actual}' .")
        
        elif command == "finish":   
            if not viaje_activo:
                print("Error: no hay un viaje en curso para finalizar.")
                continue
              
            # Agrega tiempo del último estado
            duration = time.time() - inicio_estado
            if estado_actual == "stopped":
                tiempo_parado += duration
            else:
                tiempo_movimiento += duration

            # Calcula la tarifa total y muestra el reumen del viaje
            
            total_fare = calculate_fare(tiempo_parado, tiempo_movimiento, tarifa_parado, tarifa_movimiento)

            total_duration = tiempo_parado + tiempo_movimiento
            
            guardar_historial(
                user,
                total_fare,
                total_duration,
                tiempo_parado,
                tiempo_movimiento
            )
            
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
            print("  'start' - Iniciar un nuevo viaje")
            print("  'exit'  - Salir del programa")
            print("=" * 40 + "\n")

            # Reset la svariables para el próximo viaje 
           
            viaje_activo = False
            estado_actual = None
            continue        
        
        elif command == "exit":
            confirm = input("¿Estás seguro de que deseas salir? (s/n): ").strip().lower()
            if confirm == "s":
                print("\n¡Gracias por usar el taxímetro! ¡Hasta luego!\n")
                break
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
                    print("  • 'stop'   - Detener el taxi")
                    print("  • 'move'   - Reanudar movimiento")
                    print("  • 'finish' - Finalizar el viaje actual")
                else:
                    print("  • 'start'  - Iniciar un nuevo viaje")
                print("  • 'exit'   - Salir del programa")
                print("=" * 40 + "\n")
                continue   
        
        else:
            print("Comando no reconocido. Por favor, use 'start', 'stop', 'move', 'finish' o 'exit'.")                                
import time
from datetime import datetime

def guardar_historial(username, fare, total_duration, tiempo_parado, tiempo_movimiento):
    """
    Guarda el historial de viajes en un archivo de texto plano.
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    #Creamos la línea con formato: Fecha | Usuario | Tarifa | Duración | Parado | Moviendo
    
    registro = (
        f"{fecha} - "
        f"User: {username}, "
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