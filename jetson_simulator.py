"""
Simulate the Jetsons sending status updates to the server.

Run from multiple terminals as follows:

`python script.py jetson_nano_1`

`python script.py jetson_nano_2`

`python script.py jetson_nano_3`

`python script.py jetson_nano_4`
"""

import requests
import json
import random
import time
import threading
from socketio import Client

def get_wifi_status():
    # randomly return True or False
    return True

def get_battery_level():
    # randomly return a number between 0 and 100
    return random.randint(0, 100)

def get_temperature():
    # randomly return a number between 0 and 100
    return random.randint(0, 100)

class NamespaceHandler(Client):
    def on_connect(self):
        print('Connected to the server')

    def on_disconnect(self):
        print('Disconnected from the server')

    def on_message(self, data):
        print('Received message:', data)

    def on_command(self, data):  # This function listens for the 'command' event
        print('Received command:', data)

# Device ID as a command line argument
import sys
if len(sys.argv) != 2:
    print('Usage: python script.py <device_id>')
    sys.exit(1)

deviceId = sys.argv[1]

sio = NamespaceHandler()

# Connect to the server
sio.connect('http://192.168.110.1:5000')

# Register event handlers
sio.on('connect', sio.on_connect)
sio.on('disconnect', sio.on_disconnect)
sio.on('message', sio.on_message)
sio.on('command', sio.on_command)  # Listen for 'command' event

# Emit the device_id event
sio.emit('device_id', deviceId)

# Start a new thread for periodically sending status updates
def send_status_updates():
    while True:
        try:
            data = {
                'deviceId': deviceId,
                'wifiStatus': get_wifi_status(),
                'batteryLevel': get_battery_level(),
                'temperature': get_temperature()
            }
            
            response = requests.post('http://192.168.110.1:5000/api/status', data=json.dumps(data), headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                print('Data sent successfully')
                print(data)
            else:
                print('Failed to send data')
        
        except Exception as e:
            print(f"Error: {e}")
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content}")

        time.sleep(5)  # Wait for 5 seconds before sending the next status update

status_thread = threading.Thread(target=send_status_updates)
status_thread.start()

try:
    sio.wait()
finally:
    sio.disconnect()

# TODO: I can't CTRL + C out of this script as it currently is!

# TODO: Jetson2 seems to frequently disconnect on the server... why is this? But jetson1 is always connected
#  even when I run it 2nd after jetson2... not sure what's going on here.
