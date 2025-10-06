import random
import time
import requests

def get_humidity():
    # Simulate humidity data (in %)
    return round(random.uniform(10.0, 80.0), 2)

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

# Simulate and send humidity data every 30 seconds
while True:
    humidity = get_humidity()
    send_to_local_server("humidity", humidity)
    time.sleep(10)
