# Proyecto Taxímetro

Primer proyecto desarrollado en Python para el bootcamp de Factoría F5.

## Features

- Console-based taximeter flow with login and registration
- Access event logging to `access.log`
- Persistent user storage in SQLite (`taximeter.db`)
- Trip history saved to `historial_viajes.txt`
- Python Tkinter GUI for trip control
  - Start Trip
  - Stop
  - Resume
  - Finish Trip
  - New Trip
  - Status label
  - Total fare display

## Project structure

- `taximetro.py` - existing console application and shared business logic
- `taximetro_gui.py` - new Tkinter GUI interface using shared logic
- `README.md` - project documentation
- `historial_viajes.txt` - trip history file
- `access.log` - access and security log file

## How the fare system works

The fare is calculated using two rates:

- `tarifa_parado`: price per second while stopped
- `tarifa_movimiento`: price per second while moving

Total fare formula:

```
fare = seconds_stopped * tarifa_parado + seconds_moving * tarifa_movimiento
```

The app tracks time in both stopped and moving states, then saves the result to history.

## How to run the program

### Console mode

```bash
python taximetro.py
```

### GUI mode

```bash
python taximetro_gui.py
```

## How to run tests

The project includes a basic unit test for fare calculation in `taximetro.py`.

```bash
python -m unittest taximetro.TestFareCalculation
```

## Future improvements

- Add full GUI login/registration flow
- Add better trip summary and export options
- Improve unit test coverage for state helpers and database access
- Add configurable tariff input directly in the GUI
