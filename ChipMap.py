# Required libraries and modules
import json
import sqlite3
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# Define client
client = mqtt.Client("Chip")

# Connect to the MQTT broker
client.connect("broker.hivemq.com", 1883)

# Function to store data in SQLite database
def database(data):
    # Extract data from the input array
    Id = data[0]         # Device ID
    status = data[1]     # Device Status
    latitude = data[2]   # Latitude of device
    longitude = data[3]  # Longitude of device
    timestamp = data[4]  # Date and Time of when data was collected

    # Connect to the SQLite database file
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Create the Chip table if not exists
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Chip(
        ChipID INTEGER, 
        Status BOOLEAN, 
        Latitude REAL, 
        Longitude REAL, 
        Date DATETIME,
        PRIMARY KEY (ChipID, Date))''')

    # Insert data into the database Chip table
    cursor.execute("INSERT INTO Chip values(:ChipID, :Status, :Latitude, :Longitude, :Date);", {
        "ChipID": Id,
        "Status": status,
        "Latitude": latitude,
        "Longitude": longitude,
        "Date": timestamp
    })

    # Commit the transaction (save changes to database)
    conn.commit()
    # Close the cursor and the database connection
    cursor.close()
    conn.close()

# Main function
def main():
    Id = 1   # Device ID
    status = True   # Device status

    try:
        # Read coordinates from JSON file
        with open('coordinates_map.json') as f:
            data = json.load(f)
            coordinates = data['coordinates']

        # Iterate through each coordinate
        for coord in coordinates:
            # Get current date and time
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Store ID, Status, Time, Date, and coordinates into the 'data' array
            data = [Id, status, coord['latitude'], coord['longitude'], current_time]
            # Store data in the database
            database(data)

            # Encode array 'data' into JSON data format to send it through topic
            data_encoded = json.dumps(data)
            # Publish data to topics and print
            client.publish("smarthouse/chip/data", data_encoded)
            # Print each coordinate with date and time
            print(f"Just published: Timestamp: {current_time}; data: {data_encoded} to topic: 'smarthouse/chip/data'")

            # Wait for 3 seconds before the next iteration
            time.sleep(3)

        print("Data stored in the database successfully.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    # Start the main function when the script is executed
    main()
