import time
import random
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
NIM = "2410010496"

TOPIC_SUHU = f"iot/{NIM}/sensor/suhu"
TOPIC_RELAY = f"iot/{NIM}/aktuator/relay"
TOPIC_PWM = f"iot/{NIM}/aktuator/pwm"

status_relay = "OFF"
nilai_pwm = 0

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[TERHUBUNG] Broker MQTT ({BROKER}:{PORT})")
        client.subscribe([(TOPIC_RELAY, 0), (TOPIC_PWM, 0)])
        print(f"[SUBSCRIBE] {TOPIC_RELAY} & {TOPIC_PWM}")
    else:
        print(f"[GAGAL] Kode koneksi: {reason_code}")

def on_message(client, userdata, msg):
    global status_relay, nilai_pwm
    payload = msg.payload.decode("utf-8").strip()

    if msg.topic == TOPIC_RELAY:
        status_relay = payload
        gpio_state = "HIGH (1)" if status_relay == "ON" else "LOW (0)"
        print(f"[AKTUATOR RELAY] GPIO 26 -> {status_relay} ({gpio_state})")

    elif msg.topic == TOPIC_PWM:
        try:
            nilai_pwm = max(0, min(255, int(float(payload))))
            persen = round((nilai_pwm / 255) * 100, 1)
            print(f"[AKTUATOR PWM]   GPIO 2  -> {nilai_pwm}/255 ({persen}%)")
        except ValueError:
            print(f"[ERROR] Nilai PWM tidak valid: {payload}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        # Simulasi pembacaan suhu sensor DHT22 (25.0 - 34.0 °C)
        suhu = round(random.uniform(25.0, 34.0), 1)
        client.publish(TOPIC_SUHU, str(suhu))
        print(f"[SENSOR DHT22]   Publish Suhu: {suhu} °C -> {TOPIC_SUHU}")
        time.sleep(3)  # Kirim setiap 3 detik
except KeyboardInterrupt:
    print("\nProgram dihentikan.")
    client.loop_stop()
    client.disconnect()