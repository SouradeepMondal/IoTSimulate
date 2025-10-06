import random
import time
import requests

def get_temperature():
    # Simulate temperature data (in °C)
    return round(random.uniform(10.0, 50.0), 2)

def send_to_local_server(sensor_type, value):
    url = "http://localhost:5000/sensor"
    payload = {
        "sensor_type": sensor_type,
        "value": value
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"Sent {sensor_type} data: {value}")
        print(response.json())
    else:
        print("Error sending data.")

# Simulate and send temperature data every 30 seconds
while True:
    temp = get_temperature()
    send_to_local_server("temperature", temp)
    time.sleep(10)
