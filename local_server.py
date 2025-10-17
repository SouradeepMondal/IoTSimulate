from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os # We'll use this to check if the DB file exists

app = Flask(__name__)

# Store data for multiple sensors
sensor_data = {
    "temperature",
    "humidity",
    "light"
}

# --- SQLite Setup ---
DATABASE_NAME = 'iot_readings.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_db():
    """Creates the necessary tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT file FROM pragma_database_list WHERE name = 'main';")
    db_path = cursor.fetchone()[0]
    print(f"Path of the currently connected database: {db_path}")

    # Table to store all sensor readings (Time-Series data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            timestamp TEXT NOT NULL,
            sensor_type TEXT NOT NULL,
            value REAL NOT NULL
        )
    ''')

    # Table to store server actions/trigger messages
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions_log (
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')

    # Table to store the CURRENT state of controlled devices
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_states (
            device_id TEXT PRIMARY KEY,
            state_value TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Define thresholds for triggering actions
THRESHOLDS = {
    "humidity": {"min": 40, "max": 60},  # 40% to 60% for normal humidity
    "temperature": {"min": 22, "max": 24},  # 22°C to 24°C for optimal HVAC temperature
    "light": {"min": 300, "max": 800}  # Lux value to adjust light brightness
}

def log_action(message):
    """Logs a trigger message to the database."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO actions_log (timestamp, message) VALUES (?, ?)', (timestamp, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"ERROR logging action: {e}")

def update_device_state(device_id, state_value):
    """Updates the state of a controlled device in the database."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO device_states (device_id, state_value, last_updated)
            VALUES (?, ?, ?)
            ON CONFLICT(device_id) DO UPDATE SET
                state_value = excluded.state_value,
                last_updated = excluded.last_updated
        ''', (device_id, state_value, timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"ERROR updating device state: {e}")


# Simulate actions (these will be printed or logged)
def trigger_dehumidifier(humidity):
    if humidity > THRESHOLDS["humidity"]["max"]:
        message = f"Humidity too high ({humidity}%). Turning on dehumidifier."
        log_action(message)
        update_device_state("dehumidifier", "ON")
    elif humidity < THRESHOLDS["humidity"]["min"]:
        message = f"Humidity too low ({humidity}%). Turning off dehumidifier."
        log_action(message)
        update_device_state("dehumidifier", "OFF")
    else:
        # If humidity is within range, assume it stays off/idle
        update_device_state("dehumidifier", "OFF")


def adjust_ac(temperature):
    if temperature > THRESHOLDS["temperature"]["max"]:
        temp_setting = f"COOL to {THRESHOLDS["temperature"]["min"]}°C"
        message = f"Temperature too high ({temperature}°C). Setting AC to {temp_setting}."
        log_action(message)
        update_device_state("ac", temp_setting)
    elif temperature < THRESHOLDS["temperature"]["min"]:
        temp_setting = f"HEAT to {THRESHOLDS["temperature"]["max"]}°C"
        message = f"Temperature too low ({temperature}°C). Setting AC to {temp_setting}."
        log_action(message)
        update_device_state("ac", temp_setting)
    else:
        temp_setting = "IDLE (Optimal)"
        message = f"Temperature is optimal ({temperature}°C). AC is {temp_setting}."
        log_action(message)
        update_device_state("ac", temp_setting)

def adjust_light_brightness(light_level):
    if light_level < THRESHOLDS["light"]["min"]:
        brightness_level = "100%"
        message = f"Light level low ({light_level} lux). Turning on light at {brightness_level} brightness."
        log_action(message)
        update_device_state("light", brightness_level)
    elif light_level > THRESHOLDS["light"]["max"]:
        brightness_level = "10%"
        message = f"Light level high ({light_level} lux). Dimming light to {brightness_level} brightness."
        log_action(message)
        update_device_state("light", brightness_level)
    else:
        # Calculate proportional brightness
        brightness = round((light_level - THRESHOLDS["light"]["min"]) / (THRESHOLDS["light"]["max"] - THRESHOLDS["light"]["min"]) * 100)
        brightness_level = f"{brightness}%"
        message = f"Light level is {light_level} lux. Setting light brightness to {brightness_level}."
        log_action(message)
        update_device_state("light", brightness_level)


@app.route('/')
def index():
    # return "Welcome to the Local IoT Simulator!"
    return render_template('index.html')

@app.route('/sensor', methods=['POST'])
def receive_data():
    # Receive sensor data in JSON format
    data = request.json
    
    # Extract sensor type and data
    sensor_type = data.get('sensor_type')
    sensor_value = data.get('value')
    
    if sensor_type not in sensor_data:
        return jsonify({"status": "error", "message": "Invalid sensor type"}), 400

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # # Store data in the corresponding sensor's list
    # sensor_data[sensor_type].append(sensor_value)

    # log data to sqlite
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO readings (timestamp, sensor_type, value)
            VALUES (?, ?, ?)
        ''', (timestamp, sensor_type, sensor_value))
        conn.commit()
        conn.close()
    except Exception as e:
        # Log the error but continue to process the data if possible
        print(f"ERROR inserting data into DB: {e}")
        return jsonify({"status": "error", "message": "Data received, but database write failed"}), 500

    
    # Trigger actions based on the data received
    if sensor_type == "humidity":
        trigger_dehumidifier(sensor_value)
    elif sensor_type == "temperature":
        adjust_ac(sensor_value)
    elif sensor_type == "light":
        adjust_light_brightness(sensor_value)
    
    return jsonify({"status": "success", "message": "Data received successfully!"})

@app.route('/data/<sensor_type>', methods=['GET'])
def get_data(sensor_type):
    if sensor_type not in sensor_data:
        return jsonify({"status": "error", "message": "Invalid sensor type"}), 400
    # return jsonify(sensor_data[sensor_type])
    # Retrieve the last 100 readings for the specified sensor type from SQLite
    conn = get_db_connection()
    readings = conn.execute('''
        SELECT timestamp, value 
        FROM readings 
        WHERE sensor_type = ?
        ORDER BY timestamp DESC
        LIMIT 100
    ''', (sensor_type,)).fetchall()
    conn.close()

    # Convert the list of sqlite3.Row objects to a list of dictionaries for JSON response
    data_list = [dict(row) for row in readings]
    
    return jsonify(data_list)

@app.route('/data/all', methods=['GET'])
def get_all_data():
    # Retrieve all readings (up to a limit) from the database
    conn = get_db_connection()
    readings = conn.execute('''
        SELECT timestamp, sensor_type, value 
        FROM readings 
        ORDER BY timestamp DESC
        LIMIT 500
    ''').fetchall()
    conn.close()
    
    # Convert the list of sqlite3.Row objects to a list of dictionaries for JSON response
    data_list = [dict(row) for row in readings]
    
    return jsonify(data_list)

@app.route('/actions/latest', methods=['GET'])
def get_latest_actions():
    """Retrieves the latest 20 server actions/trigger messages."""
    conn = get_db_connection()
    actions = conn.execute('''
        SELECT timestamp, message 
        FROM actions_log 
        ORDER BY timestamp DESC
        LIMIT 20
    ''').fetchall()
    conn.close()
    
    # Convert to list of dictionaries for JSON response
    data_list = [dict(row) for row in actions]
    
    return jsonify(data_list)

@app.route('/states', methods=['GET'])
def get_device_states():
    """Retrieves the current state of all controlled devices."""
    conn = get_db_connection()
    states = conn.execute('SELECT device_id, state_value, last_updated FROM device_states').fetchall()
    conn.close()
    
    # Convert to a dictionary for easy client-side lookup
    # e.g., {"light": "100%", "ac": "COOL to 24°C", ...}
    states_dict = {row['device_id']: {'value': row['state_value'], 'updated': row['last_updated']} for row in states}
    
    return jsonify(states_dict)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
