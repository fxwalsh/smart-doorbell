#!/usr/bin/env python3
import time, json, os
from datetime import datetime

from sense_hat import SenseHat
from picamera2 import Picamera2
from upload_to_cloudinary import upload_image

import paho.mqtt.client as mqtt

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "/fxwalsh/event/doorbell"  # change to your own ID

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

sense = SenseHat()
sense.clear(0, 0, 0)

picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
print("Camera started. Press the Sense HAT joystick (middle) to take a photo.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATE_DIR = os.path.join(BASE_DIR, "state")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

IMAGE_PATH = os.path.join(STATIC_DIR, "last_visitor.jpg")
STATE_PATH = os.path.join(STATE_DIR, "doorbell.json")

def save_state():
    now = datetime.now()
    celcius = round(sense.temperature, 2)
    payload = {
        "celcius": round(celcius, 2),
        "fahrenheit": round(1.8 * celcius + 32, 2),
        "ts": int(now.timestamp()),
        "iso": now.isoformat(timespec="seconds")
    }
    with open(STATE_PATH, "w") as f:
        json.dump(payload, f)
    print("State saved:", payload)


def capture_photo():
    print("Capturing visitor photo...")
    picam2.capture_file(IMAGE_PATH)
    sense.clear(0, 255, 0)  # flash green
    time.sleep(0.3)
    sense.clear(0, 0, 0)
    print("Photo saved to:", IMAGE_PATH)
    save_state()
    url = upload_image(IMAGE_PATH)
    payload = {
        "event": "doorbell_pressed",
        "ts": int(time.time()),
        "url" : url
    }
    client.publish(MQTT_TOPIC, json.dumps(payload))
    print("MQTT event published:", payload)
 
   
    


try:
    while True:
        for event in sense.stick.get_events():
            if event.action == "pressed" and event.direction == "middle":
                print("Doorbell pressed at", datetime.now())
                capture_photo()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    picam2.stop()
    sense.clear()
    client.loop_stop()
    client.disconnect()