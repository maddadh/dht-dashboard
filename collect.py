import os, csv, ssl, time, json
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

HOST  = os.environ["MQTT_HOST"]
PORT  = int(os.environ["MQTT_PORT"])
USER  = os.environ["MQTT_USER"]
PASS  = os.environ["MQTT_PASS"]
T_TEMP = os.environ["TOPIC_TEMP"]
T_HUM  = os.environ["TOPIC_HUM"]

readings = {}

def on_connect(client, userdata, flags, rc, props=None):
    client.subscribe(T_TEMP)
    client.subscribe(T_HUM)

def on_message(client, userdata, msg):
    topic = msg.topic.lower()
    raw   = msg.payload.decode().strip()
    try:
        val = float(json.loads(raw)) if raw.startswith("{") else float(raw)
    except Exception:
        return

    if topic.endswith("/temperature"):
        readings["temp_f"] = round(val * 9 / 5 + 32, 2)
    elif topic.endswith("/humidity"):
        readings["hum"] = round(val, 2)

    if "temp_f" in readings and "hum" in readings:
        client.disconnect()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USER, PASS)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.on_connect = on_connect
client.on_message = on_message

client.connect(HOST, PORT, keepalive=30)
client.loop_start()

# Wait up to 20 seconds for both readings
for _ in range(40):
    if "temp_f" in readings and "hum" in readings:
        break
    time.sleep(0.5)

client.loop_stop()

if "temp_f" in readings and "hum" in readings:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open("data.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([ts, readings["temp_f"], readings["hum"]])
    print(f"✅ Appended: {ts}, {readings['temp_f']}°F, {readings['hum']}%")
else:
    print("⚠️ Timeout — no readings received, CSV not updated")
