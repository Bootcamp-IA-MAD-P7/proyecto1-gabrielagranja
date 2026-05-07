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
if __name__ == "__main__":
    calculate_fare(10, 20)
    
