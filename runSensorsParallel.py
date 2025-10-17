import subprocess
import time

scripts = ['humidity_sensor.py', 'lumen_sensor.py', 'temp_sensor.py']

# Start each script in a separate process
processes = []
for script in scripts:
    process = subprocess.Popen(['python', script])
    processes.append(process)
    print(f"Started {script} in a separate process.")

# Keep the main script running until any of the processes are interrupted
try:
    # Wait for all processes to complete (they run indefinitely unless stopped manually)
    while True:
        time.sleep(1)  # Sleep to prevent high CPU usage in the loop
except KeyboardInterrupt:
    print("Terminating all scripts...")
    # Terminate all subprocesses gracefully
    for process in processes:
        process.terminate()
    for process in processes:
        process.wait()  # Wait for each process to terminate properly
    print("All scripts have been terminated.")
