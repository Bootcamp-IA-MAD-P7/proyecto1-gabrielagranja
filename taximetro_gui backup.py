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
)

class TaximeterGUI(tk.Tk):
    """Simple Tkinter GUI for the taximeter trip flow."""

    def __init__(self):
        super().__init__()
        self.title("Taxímetro GUI")
        self.resizable(False, False)
        self.state = create_trip_state()
        self.tarifa_parado = DEFAULT_TARIFA_PARADO
        self.tarifa_movimiento = DEFAULT_TARIFA_MOVIMIENTO
        self.username = "GUI"
        self._build_widgets()
        self._update_ui()

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

    def _show_message(self, title, text, level="info"):
        if level == "error":
            messagebox.showerror(title, text)
        else:
            messagebox.showinfo(title, text)

    def on_start(self):
        if start_trip_state(self.state):
            log_access_event(self.username, "GUI_TRIP_START", True, "Trip started")
            self._update_ui()
        else:
            self._show_message("Trip already active", "A trip is already active. Use Finish Trip or New Trip.")

    def on_stop(self):
        if stop_trip_state(self.state):
            log_access_event(self.username, "GUI_TRIP_STOP", True, "Trip stopped")
            self._update_ui()
        else:
            self._show_message("Cannot stop", "There is no active moving trip to stop.", level="error")

    def on_resume(self):
        if resume_trip_state(self.state):
            log_access_event(self.username, "GUI_TRIP_RESUME", True, "Trip resumed")
            self._update_ui()
        else:
            self._show_message("Cannot resume", "There is no stopped trip to resume.", level="error")

    def on_finish(self):
        result = finish_trip_state(self.state, self.tarifa_parado, self.tarifa_movimiento, self.username)
        if result is None:
            self._show_message("No active trip", "There is no active trip to finish.", level="error")
            return
        fare_text = f"Trip finished. Total fare: € {result['total_fare']:.2f}\nTotal duration: {result['total_duration']:.1f} s"
        log_access_event(self.username, "GUI_TRIP_FINISH", True, f"Fare: {result['total_fare']:.2f}")
        self._show_message("Trip finished", fare_text)
        self._update_ui()

    def on_new_trip(self):
        reset_trip_state(self.state)
        log_access_event(self.username, "GUI_TRIP_RESET", True, "New trip state initialized")
        self._update_ui()


def main():
    app = TaximeterGUI()
    app.geometry("600x600")  # Tamaño de la ventana
    app.configure(bg="#f0f0f0")  # Fondo claro  
    app.option_add("*Font", "Arial 12")  # Fuente global para la aplicación 
    app.option_add("*Button.Background", "#4CAF50")  # Color de fondo de los botones
    app.option_add("*Button.Foreground", "white")  # Color del texto de los botones 
    app.option_add("*Button.ActiveBackground", "#45a049")  # Color de fondo al hacer clic en los botones
    app.option_add("*Label.Background", "#f0f0f0")  # Fondo de las etiquetas    
    app.mainloop() # Cambia la estética


if __name__ == "__main__":
    main()
