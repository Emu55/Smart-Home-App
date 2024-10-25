import flask
from datetime import datetime
import folium
import sqlite3
import os
import subprocess

app = flask.Flask(__name__)

# Define a global variable to store the PID of the chipmap.py process
chipmap_pid = None

# Function to check if map file is created, if not, create it
def check_map_file():
    if not os.path.exists('static/map.html'):
        map = folium.Map(location=[52.178219, -1.667904], zoom_start=10)

        # Save the map to an HTML file
        filename = 'static/map.html'
        map.save(filename)
        print("Map saved to:", filename)
    else:
        pass

# Function to fetch coordinates from the database
def fetch_coordinates_from_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT Latitude, Longitude FROM Chip")
    coordinates = cursor.fetchall()
    conn.close()
    return coordinates

# Function to visualize coordinates on the map
def visualize_coordinates_on_map(coordinates):
    map = folium.Map(location=[52.178219, -1.667904], zoom_start=10)

    # Add markers for each coordinate on map
    for coord in coordinates:
        folium.Marker([coord[0], coord[1]]).add_to(map)

    # Save the map to an HTML file
    map_filename = 'static/map.html'
    map.save(map_filename)
    print("Map updated and saved to:", map_filename)


''' API Endpoints '''

# Get the chip status
@app.route('/chip_status', methods=['GET'])
def chip_status():
    global chipmap_pid
    
    try:
        # Define the PowerShell command to retrieve all processes
        powershell_cmd = "Get-WmiObject Win32_Process | Select-Object ProcessId, CommandLine"

        # Execute the PowerShell command to retrieve all processes
        process = subprocess.Popen(["powershell.exe", "-Command", powershell_cmd], stdout=subprocess.PIPE, shell=True)
        output, _ = process.communicate()

        # Decode the output from bytes to string
        process_output = output.decode('utf-8')

        # Split the output by lines and iterate over each line
        for line in process_output.split('\n'):
            # Skip empty lines
            if not line.strip():
                continue
            # Split the line into ProcessId and CommandLine
            parts = line.strip().split(" ", 1)
            process_id = parts[0]
            command_line = parts[1] if len(parts) > 1 else ''
            # Check if the command line matches the expected one
            if command_line.strip() == '"C:\\Program Files\\Python311\\python.exe" .\\ChipMap.py':
                chipmap_pid = process_id
                return f"ChipMap.py is running with PID: {chipmap_pid}"
        else:
            return "ChipMap.py is not running"
    except Exception as e:
        return str(e)


# NOT WORKING - start chipmap.py
@app.route('/start_chipmap', methods=['GET'])
def start_chipmap():
    global chipmap_pid
    try:
        # Check if ChipMap.py is already running
        if chipmap_pid:
            return f"chipmap.py is already running with PID: {chipmap_pid}"
        else:
            # Start ChipMap.py with the desired command line
            command_line = f'"C:\\Program Files\\Python311\\python.exe" .\\ChipMap.py'
            process = subprocess.Popen(command_line, shell=True)
            chipmap_pid = process.pid
            return f"ChipMap.py started with PID: {chipmap_pid}"
    except Exception as e:
        return str(e)

# stop chipmap.py
@app.route('/stop_chipmap', methods=['GET'])
def stop_chipmap():
    global chipmap_pid
    try:
        # Check if ChipMap.py is already running
        if chipmap_pid:
            # Stop ChipMap.py
            process = subprocess.Popen(["taskkill", "/F", "/PID", chipmap_pid])
            process.communicate()
            chipmap_pid = None
            return "ChipMap.py stopped successfully"
        else:
            return "chipmap.py is not running"
    except Exception as e:
        return str(e)

# Route to update the map with new coordinates
@app.route('/update_map', methods=['GET'])
def update_map():
    # Check if the map file exists
    check_map_file()
    # Fetch coordinates from the database
    coordinates = fetch_coordinates_from_db()
    # Visualize coordinates on the map
    visualize_coordinates_on_map(coordinates)
    return "Map updated successfully"

# Route for the index page
@app.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html')

if __name__ == '__main__':
    check_map_file()
    app.run()
