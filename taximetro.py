import time

def calculate_fare(seconds_stopped, seconds_moving):
    """""
    Calcular la tarifa total en euros.
    - Stopped: 0.02 €/s
    - Moving: 0.05 €/s
    """

    fare = seconds_stopped*0.02 + seconds_moving *0.05
    print(f"Total: {fare} €")
    return fare

def taximeter():
    """
    Función para mostrar las opciones del taxímetro.
    """
    print ("Hola")
    print ("Escoge una de las siguientes opciones: 'start', 'stop', 'move', 'finish','exit'\n")
    
    # Declaración de variables para contar el tiempo detenido y en movimiento
    #trip_active, viaje_activo, Hay un viaje en curso
    #stopped_time, tiempo_parado, Tiempo acumulado parado
    #moving_time, tiempo_movimiento, Tiempo acumulado moviéndose
    #state, estado_actual, Estado actual del taxi
    #state_start_time, inicio_estado, Cuándo empezó ese estado
    #start_time, inicio_viaje, Cuándo empezó el viaje


    viaje_activo = False
    inicio_viaje = 0
    tiempo_parado = 0
    tiempo_movimiento = 0
    estado_actual = None # 'stopped' o 'moving'
    inicio_viaje = 0

# Codificando el event loop 
    
    while True:
        command = input("> ").strip().lower()

        if command == "start":
            if viaje_activo:
                print("Error: un  viaje en curso. ")
                continue
            viaje_activo = True
            inicio_viaje = time.time()
            tiempo_parado = 0
            tiempo_movimiento = 0
            estado_actual = "s"
            inicio_estado = time.time()

            print("Viaje iniciado. EStado incial: 'stopped'")

        elif command == ("stop", "move"):
            if not viaje_activo:
                print("Error: no hay un viaje en curso. Por favor empie un viaje con 'start'.")
                continue

            #calcula el tiempo transcurrido en el estado actual antes de cambiar
            
            duration= time.time() - inicio_estado
                
            if estado_actual == "stopped":
                    tiempo_parado += duration
            else:
                    tiempo_movimiento += duration

            # Cambo el estado actual y reinicia el tiempo de inicio del estado
            estado_actual == "stopped" if command == "stop" else "moving"
            inicio_estado = time.time()
            
            print(f"state changed to '{estado_actual} .")
        
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
            
            total_fare = calculate_fare(tiempo_parado, tiempo_movimiento)
            print("\n--- Resumen de tu Viaje ---")
            print(f"Tiempo parado: {tiempo_parado:.1f} s")
            print(f"Tiempo en movimiento: {tiempo_movimiento:.1f} s")
            print(f"total_fare: € {total_fare:.2f}")
            print("-------------------------------\n")

            print("Inicia un nuevo viaje con 'start' o salir con 'exit'.")

            #Reset la svariables para el próximo viaje 
            trip_active = False
            estado_actual = None        
        
        elif command == "exit":
            print("Saliendo del taxímetro. ¡Hasta luego!")
            break   
        
        else:
            print("Comando no reconocido. Por favor, use 'start', 'stop', 'move', 'finish' o 'exit'.")                                
                                       
if __name__ == "__main__":
    taximeter()