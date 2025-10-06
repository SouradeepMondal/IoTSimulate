import random
import time
import requests

def get_light_level():
    # Simulate light level data (in lux)
    return round(random.uniform(100, 1000), 2)

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

# Simulate and send light level data every 30 seconds
while True:
    light_level = get_light_level()
    send_to_local_server("light", light_level)
    time.sleep(20)
