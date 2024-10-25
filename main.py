import paho.mqtt.client as mqtt
import sqlite3  # import sqlite
from datetime import date, datetime
import json


# function to connect with topic
def on_connect(client, userdata, flags, rc):  # client method to connect

    if rc == 0:
        print("connected OK Returned code=", rc)  # let us know we connected to the broker

        # TOPICS MUST BE ADDED HERE
        client.subscribe("smarthouse/sensors/temperature")
        client.subscribe("smarthouse/sensors/motion")
        client.subscribe("smarthouse/cameras/data")
        client.subscribe("smarthouse/doorlock/data")
        client.subscribe("smarthouse/chip/data")
        # topic

    else:
        print("Bad connection Returned code=", rc)  # if we can't connect


# function to receive messages
def on_message(client, userdata, msg, ):  # client method to get messages from topic
    topic = msg.topic  # for use when we can't decode

    try:
        day = date.today()  # date function call
        clock = datetime.now()  # time function calls
        time_time = datetime.time(clock)

        # DECODING CODE GOES HERE FOR EACH SEPARATE TOPIC
        if topic == "smarthouse/sensors/temperature":  # decodes message from specific topic (sensors)
            data = json.loads(msg.payload.decode("utf-8"))  # decode message, turns it back into array 'data'

            # insert data into database
            connect_db = sqlite3.connect('database.db')  # connect to database
            cursor = connect_db.cursor()  # define cursor
            # transfer data from array to new row in the temperature_sensors table
            cursor.execute("INSERT INTO temperature_sensors VALUES (:ID, :DATE, :TIME, :LOCATION, :TEMPERATURE)", {
                "ID": data[0],
                "DATE": data[1],
                "TIME": data[2],
                "LOCATION": data[3],
                "TEMPERATURE": data[4]

            })
            connect_db.commit()  # commit changes to database
            connect_db.close()  # close database
        # Zeyd's
        if topic == "smarthouse/cameras/data":  # decodes message from specific topic (sensors)
            data = json.loads(msg.payload.decode("utf-8"))  # decode message, turns it back into array 'data'

            # stores data from arrays to variables
            Id = data[0]
            status = data[1]
            location = data[2]
            day = data[3]
            time_time = data[4]
            video_data = bytearray(data[5])

            try:
                # Connecting to the database
                conn = sqlite3.connect('database.db')
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT INTO Camera VALUES (:id, :Cam_Status, :Cam_location, :Clip_Date, :Clip_Time, :Clip)", {
                        "id": Id,
                        "Cam_Status": status,
                        "Cam_location": location,
                        "Clip_Date": day,
                        "Clip_Time": time_time,
                        "Clip": str(video_data)
                    })
                conn.commit()
                conn.close()
                print("Succesfully inserted in database. \n")

            except Exception as e:
                print(f"Failed to insert in database. Error: {str(e)}\n")

            try:
                # Decoding the video file
                output_path = '/Users/zeydajraou/Documents/IDC/Decoded/output_photo.jpeg'

                with open(output_path, 'wb') as video_file:
                    video_file.write(video_data)
                print(f"Video Successfully decoded in folder {output_path}\n")

            except Exception as e:
                print(f"Failed to decode the video. Error: {str(e)}\n")

            # Stefan's
        if topic == "smarthouse/sensors/motion":
            data = json.loads(msg.payload.decode("utf-8"))
            location = data["location"]
            motion_detected = data["motion_detected"]

        # Milo
        if topic == "smarthouse/doorlock/data":  # decodes message from specific topic (sensors)
            data = json.loads(msg.payload.decode("utf-8"))  # decode message, turns it back into array 'data'
            # stores data from arrays to variables
            fingerprint = data[0]  # example: database.Id = data[0]
            lock_action = data[1]
            timestamp = data[2]

        # Aymen
        if topic == "smarthouse/chip/data":
            data = json.loads(msg.payload.decode("utf-8"))

        # print message with data, time and date to check if it is received and decoded
        print("Received message at : date-" + str(day) + " time-" + str(
            time_time) + " / data: topic: " + topic + ";  value: "
              + str(data))

    except:
        print("Cannot decode data on topic:" + topic)  # cannot decode; print the topic for the non-decodable message


# define client
client = mqtt.Client()

# callback functions
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883)  # connect to the broker on an appropriate port

client.loop_forever()  # keep looping forever (allows realtime subscription)