#!/usr/bin/env python3
import time, json, os
from datetime import datetime

from sense_hat import SenseHat
from picamera2 import Picamera2

import paho.mqtt.client as mqtt
import requests  # <--- NEW

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "/fxwalsh/event/doorbell"  # change to your own ID

# -------- ThingSpeak config (NEW) --------
THINGSPEAK_WRITE_KEY = "WBCSK3BT4CL1TIJH"
THINGSPEAK_URL = "https://api.thingspeak.com/update"
# ---------- ThingSpeak Alerts config (NEW) ----------
THINGSPEAK_ALERTS_KEY = "TAKWohhuu2eU7KKVsft"  # <-- your Alerts API key
THINGSPEAK_ALERTS_URL = "https://api.thingspeak.com/alerts/send"
# ----------------------------------------------------
# -----------------------------------------

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

IMAGE_PATH = "static/last_visitor.jpg"

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

def send_to_thingspeak(snapshot_url=None):
    """
    Log a doorbell press to ThingSpeak.
    field1: 1 (doorbell pressed)
    field2: Unix timestamp
    field3: snapshot URL (if provided)
    """
    now_ts = int(time.time())
    params = {
        "api_key": THINGSPEAK_WRITE_KEY,
        "field1": 1,          # doorbell pressed
        "field2": now_ts,     # when it happened
    }
    if snapshot_url is not None:
        params["field3"] = snapshot_url  # store URL as text

    try:
        r = requests.get(THINGSPEAK_URL, params=params, timeout=5)
        print("ThingSpeak response:", r.text)  # entry id or '0'
    except Exception as e:
        print("Error sending to ThingSpeak:", e)

def send_email_alert(snapshot_url=None):
    """
    Send an email via ThingSpeak Alerts each time the doorbell is pressed.
    Email goes to the address on your ThingSpeak/MathWorks account.
    """
    alert_subject = "Doorbell pressed"
    alert_body = f"The doorbell was pressed at {datetime.now().isoformat(timespec='seconds')}."

    if snapshot_url:
        alert_body += f"\nLast visitor image: {snapshot_url}"

    headers = {
        "ThingSpeak-Alerts-API-Key": THINGSPEAK_ALERTS_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "subject": alert_subject,
        "body": alert_body,
    }

    try:
        r = requests.post(THINGSPEAK_ALERTS_URL,
                          headers=headers,
                          data=json.dumps(data),
                          timeout=5)
        print("Alert email response:", r.text)
    except Exception as e:
        print("Error sending alert email:", e)

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
    payload = {
        "event": "doorbell_pressed",
        "ts": int(time.time())
    }
    client.publish(MQTT_TOPIC, json.dumps(payload))
    print("MQTT event published:", payload)

    # ---- NEW: send to ThingSpeak ----
    # This URL should be how a browser reaches that image.
    # Adjust to whatever your Flask/web server serves, e.g.:
    snapshot_url = "http://hdiprpi.local:8000/static/last_visitor.jpg"
    send_to_thingspeak(snapshot_url)
    send_email_alert(snapshot_url)
    # ---------------------------------
    


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