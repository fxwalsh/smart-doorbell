#!/usr/bin/env python3
import os, json, time, datetime
from flask import Flask, render_template_string

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
STATE_PATH = os.path.join(STATE_DIR, "doorbell.json")

app = Flask(__name__, static_folder="static")

TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Smart Doorbell</title>
  <meta http-equiv="refresh" content="10">
  <style>
    body { font-family: sans-serif; max-width: 640px; margin: 2rem auto; text-align: center; }
    img  { max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 0 12px rgba(0,0,0,0.25); }
    .meta { margin-top: 1rem; color: #444; }
  </style>
</head>
<body>
  <h1>Smart Doorbell</h1>

  {% if last_event %}
    <p class="meta">
      Last press: <strong>{{ last_event.time_str }}</strong><br>
      ({{ last_event.age }} seconds ago)
    </p>
    <img src="{{ url_for('static', filename='last_visitor.jpg') }}?v={{ cache_bust }}"
         alt="Last visitor">
  {% else %}
    <p>No doorbell presses recorded yet.</p>
  {% endif %}
</body>
</html>
"""

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
    return render_template_string(
        TEMPLATE,
        last_event=last_event,
        cache_bust=int(time.time())
    )

if __name__ == "__main__":
    # Listen on all interfaces so you can access this from your laptop/phone
    app.run(host="0.0.0.0", port=8000)