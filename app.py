from flask import Flask, render_template, redirect, url_for
from taximetro_core import (
    create_trip_state,
    start_trip_state,
    stop_trip_state,
    resume_trip_state,
    finish_trip_state,
    calculate_fare,
    DEFAULT_TARIFA_PARADO,
    DEFAULT_TARIFA_MOVIMIENTO,
)

app = Flask(__name__)

trip_state = create_trip_state()
last_result = None


@app.route("/")
def home():
    fare = calculate_fare(
        trip_state["stopped_time"],
        trip_state["moving_time"],
        DEFAULT_TARIFA_PARADO,
        DEFAULT_TARIFA_MOVIMIENTO
    )

    return render_template(
        "index.html",
        state=trip_state,
        fare=fare,
        result=last_result
    )


@app.route("/start")
def start():
    start_trip_state(trip_state)
    return redirect(url_for("home"))


@app.route("/stop")
def stop():
    stop_trip_state(trip_state)
    return redirect(url_for("home"))


@app.route("/move")
def move():
    resume_trip_state(trip_state)
    return redirect(url_for("home"))


@app.route("/finish")
def finish():
    global last_result

    last_result = finish_trip_state(
        trip_state,
        DEFAULT_TARIFA_PARADO,
        DEFAULT_TARIFA_MOVIMIENTO,
        username="WEB"
    )

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)