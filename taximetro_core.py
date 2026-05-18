import time
from datetime import datetime

DEFAULT_TARIFA_PARADO = 0.02
DEFAULT_TARIFA_MOVIMIENTO = 0.05


def calculate_fare(seconds_stopped, seconds_moving, tarifa_parado, tarifa_movimiento):
    fare = seconds_stopped * tarifa_parado + seconds_moving * tarifa_movimiento
    return fare


def update_state_duration(estado_actual, inicio_estado, tiempo_parado, tiempo_movimiento):
    duration = time.time() - inicio_estado

    if estado_actual == "detenido":
        tiempo_parado += duration
    else:
        tiempo_movimiento += duration

    return tiempo_parado, tiempo_movimiento


def create_trip_state():
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
    if state["active"]:
        return False

    now = time.time()

    state.update({
        "active": True,
        "start_time": now,
        "stopped_time": 0.0,
        "moving_time": 0.0,
        "status": "movimiento",
        "status_start_time": now,
        "finished": False,
    })

    return True


def stop_trip_state(state):
    if not state["active"] or state["status"] == "detenido":
        return False

    state["stopped_time"], state["moving_time"] = update_state_duration(
        state["status"],
        state["status_start_time"],
        state["stopped_time"],
        state["moving_time"]
    )

    state["status"] = "detenido"
    state["status_start_time"] = time.time()

    return True


def resume_trip_state(state):
    if not state["active"] or state["status"] == "movimiento":
        return False

    state["stopped_time"], state["moving_time"] = update_state_duration(
        state["status"],
        state["status_start_time"],
        state["stopped_time"],
        state["moving_time"]
    )

    state["status"] = "movimiento"
    state["status_start_time"] = time.time()

    return True


def finish_trip_state(state, tarifa_parado, tarifa_movimiento, username="WEB"):
    if not state["active"]:
        return None

    state["stopped_time"], state["moving_time"] = update_state_duration(
        state["status"],
        state["status_start_time"],
        state["stopped_time"],
        state["moving_time"]
    )

    total_duration = state["stopped_time"] + state["moving_time"]
    total_fare = calculate_fare(
        state["stopped_time"],
        state["moving_time"],
        tarifa_parado,
        tarifa_movimiento
    )

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
    state.update(create_trip_state())
    return state