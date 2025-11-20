#!/usr/bin/env python3
import os, json, time, datetime
from flask import Flask, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
STATE_PATH = os.path.join(STATE_DIR, "doorbell.json")

app = Flask(__name__, static_folder="static")

def load_state():
    try:
        with open(STATE_PATH) as f:
            data = json.load(f)
        ts = data.get("ts")
        if not ts:
            return None
        age = int(time.time()) - ts
        time_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        data["age"] = age
        data["time_str"] = time_str
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        print("Error loading state:", e)
        return None

@app.route("/")
def index():
    last_event = load_state()
    return render_template(
        'status.html',
        last_event=last_event
    )

if __name__ == "__main__":
    # Listen on all interfaces so you can access this from your laptop/phone
    app.run(host="0.0.0.0", port=8000)