import time
import tkinter as tk
from tkinter import messagebox

from taximetro import (
    calculate_fare,
    create_trip_state,
    start_trip_state,
    stop_trip_state,
    resume_trip_state,
    finish_trip_state,
    reset_trip_state,
    DEFAULT_TARIFA_PARADO,
    DEFAULT_TARIFA_MOVIMIENTO,
    log_access_event,
    init_database,
)

class TaximeterGUI(tk.Tk):

    # INICIALIZACION 
    def __init__(self):
        super().__init__()
        
        self.title("Taxímetro")
        self.geometry("600x600")
        self.resizable(False, False)

        init_database()
        
        self.tarifa_parado = DEFAULT_TARIFA_PARADO
        self.tarifa_movimiento = DEFAULT_TARIFA_MOVIMIENTO
        self.state = create_trip_state()
        self.tarifa_parado = DEFAULT_TARIFA_PARADO
        self.tarifa_movimiento = DEFAULT_TARIFA_MOVIMIENTO
        self.username = "GUI"

        self.show_home_screen()

    # Configuración de la venta principal
    def show_home_screen(self):
        tk.Label(self,text= "BIENVENIDO", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Button(self, text="Iniciar Sesión", width=25, command=self.show_login_screen).pack(pady=10)  

    #LIMPIAR LA PANTALLA
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
    #MUESTRA PANTALLA DE LOGIN
    def show_login_screen(self):
        self.clear_window()

        tk.Label(self,text= "LOGIN - SISTEMA DE TAXÍMETRO", font=("Arial", 18, "bold")).pack(pady=20)
        tk.Label(self, text="Usuario:").pack()
        self.username_entry = tk.Entry(self,width=30)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Contraseña:").pack()
        self.password_entry = tk.Entry(self, show="*", width=30)
        self.password_entry.pack(pady=5)
        
        tk.Button(self, text="Iniciar Sesión", width=25, command=self.handle_login).pack(pady=10)
    #VALIDA EL LOGIN 
    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if username and password:
            self.username = username
            messagebox.showinfo("Login exitoso", f"Bienvenido, {username}!")
            self.show_trip_screen()
        else:messagebox.showerror("Error de Login", "Por favor, ingrese un usuario y contraseña válidos.")
    
    #MUESTRA LA PANTALLA PRINCIPAL DEL TAXIMETRO
    def show_trip_screen(self): 
        self.clear_window()
        self._build_widgets()
        self._update_ui()

    #CONSTRUYE LOS WIDGETS DE LA PANTALLA PRINCIPAL
    def _build_widgets(self):
        self.status_var = tk.StringVar()
        self.fare_var = tk.StringVar()

        header = tk.Label(self, text="Taxímetro", font=("Arial", 16, "bold"))
        header.grid(row=0, column=0, columnspan=2, padx=12, pady=10)

        tk.Label(self, text="Estado:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=12)
        tk.Label(self, textvariable=self.status_var, font=("Arial", 10), fg="blue").grid(row=1, column=1, sticky="w")
        tk.Label(self, text="Total fare:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=12)
        tk.Label(self, textvariable=self.fare_var, font=("Arial", 10), fg="green").grid(row=2, column=1, sticky="w")

        button_frame = tk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=14)

        tk.Button(button_frame, text="Empezar Viaje", width=12, command=self.on_start).grid(row=0, column=0, padx=6, pady=4)
        tk.Button(button_frame, text="Parar", width=12, command=self.on_stop).grid(row=0, column=1, padx=6, pady=4)
        tk.Button(button_frame, text="Resume", width=12, command=self.on_resume).grid(row=1, column=0, padx=6, pady=4)
        tk.Button(button_frame, text="Finalizar Viaje ", width=12, command=self.on_finish).grid(row=1, column=1, padx=6, pady=4)
        tk.Button(button_frame, text="Nuevo Viaje", width=26, command=self.on_new_trip).grid(row=2, column=0, columnspan=2, padx=6, pady=4)

        footer = tk.Label(self, text=f"Tarifa parada: {self.tarifa_parado:.2f} €/s | Tarifa movimiento: {self.tarifa_movimiento:.2f} €/s", font=("Arial", 8))
        footer.grid(row=4, column=0, columnspan=2, pady=6)
    #CALCULA LOS TOTALES
    def _current_trip_totals(self):
        stopped = self.state["stopped_time"]
        moving = self.state["moving_time"]
        if self.state["active"] and self.state["status"] is not None:
            elapsed = time.time() - self.state["status_start_time"]
            if self.state["status"] == "detenido":
                stopped += elapsed
            else:
                moving += elapsed
        return stopped, moving
    
    #ACTUALIZA LA INTERFAZ DE USUARIO
    def _update_ui(self):

        if self.state["active"]:
            self.status_var.set(f"Active ({self.state['status']})")
        elif self.state["finished"]:
            self.status_var.set("Trip finished")
        else:
            self.status_var.set("No active trip")

        stopped, moving = self._current_trip_totals()
        current_fare = calculate_fare(stopped, moving, self.tarifa_parado, self.tarifa_movimiento)
        self.fare_var.set(f"€ {current_fare:.2f}")
    # MENSAJES EMERGENTES
    def _show_message(self, title, text, level="info"):
        if level == "error":
            messagebox.showerror(title, text)
        else:
            messagebox.showinfo(title, text)
    #ACCIONES DE LOS BOTONES
    def on_start(self):
        if start_trip_state(self.state):
            log_access_event(self.username, "GUI_TRIP_START", True, "Viaje Iniciado")
            self._show_message("Viaje Iniciado", "El viaje ha comenzado exitosamente.")
            self._update_ui()
        else:
            self._show_message("Viaje activo", "Hay un viaje en curso. Finaliza el viaje o inicia uno nuevo.", level="error")

    def on_stop(self):
        if stop_trip_state(self.state):
            log_access_event(self.username, "GUI_TRIP_STOP", True, "Viaje detenido")
            self._show_message("Viaje detenido", "El viaje ha sido detenido.")
            self._update_ui()
        else:
            self._show_message("Cannot stop", "There is no active moving trip to stop.", level="error")

    def on_resume(self):
        if resume_trip_state(self.state):
            log_access_event(self.username, "GUI_TRIP_RESUME", True, "Viaje reanudado")
            self._show_message("Viaje reanudado", "El viaje ha sido reanudado.")
            self._update_ui()
        else:
            self._show_message("Cannot resume", "There is no stopped trip to resume.", level="error")

    def on_finish(self):
        result = finish_trip_state(self.state, self.tarifa_parado, self.tarifa_movimiento, self.username)
        if result is None:
            self._show_message("Sin viaje activo", "No hay un viake activo para terminar.", level="error")
            return
        fare_text = f"Trip finished. Total fare: € {result['total_fare']:.2f}\nTotal duration: {result['total_duration']:.1f} s"
        
        log_access_event(self.username, "GUI_TRIP_FINISH", True, f"Fare: {result['total_fare']:.2f}")
        self._show_message("Viaje finalizado", fare_text)
        self._update_ui()

    def on_new_trip(self):
        reset_trip_state(self.state)
        log_access_event(self.username, "GUI_TRIP_RESET", True, "New trip state initialized")
        self._update_ui()

def main():
    app = TaximeterGUI()
    app.geometry("600x600")  # Tamaño de la ventana
    app.configure(bg="#f0f0f0")
    app.option_add("*Font", "Arial 12")  
    app.mainloop() # Cambia la estética

if __name__ == "__main__":
    main()
