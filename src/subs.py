import time
import pandas as pd
import random
import time
from paho.mqtt import client as mqtt_client
from utils import read_report
from utils import line_to_json
import json





FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

#def on_disconnect(client, userdata, rc):
def on_disconnect(client, userdata, flags, rc, properties):
    print("Disconnected with result code: %s", rc, flush=True)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        print("Reconnecting in %d seconds...", reconnect_delay, flush=True)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            print("Reconnected successfully!", flush=True)
            return
        except Exception as err:
            print("%s. Reconnect failed. Retrying...", err, flush=True)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    print("Reconnect failed after %s attempts. Exiting...", reconnect_count, flush=True)







broker = '172.17.0.2' #
port = 1883 #
#Madrid/Moncloa/__Ines__'vitals/SpO2'   'vitals/temp'  'vitals/hr' 'vitals/resp'
topic_sub = 'rserG10/vitals' #
topic_alerts = 'rserG10/alerts' 
# topic_alerts_hr = 'alerts/hr'
# topic_alerts_temp = 'alerts/temp'
# topic_alerts_spo2 = 'alerts/SpO2'
# topic_alerts_resp = 'alerts/resp'
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
username = 'admin'
password = 'public'

HR_MEDIO = 89

TEMP_LIMITE = 37.00

SPO2_LIMITE = 95

RESP_INF = 12

RESP_SUP = 20

def connect_mqtt():
    #def on_connect(client, userdata, flags, rc):
    
    def on_connect(client, userdata, flags, rc, properties=None):
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    # def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print(f"Connected to MQTT Broker!. Subscribing to {topic_sub}...", flush=True)
            client.subscribe(topic_sub, qos=1)
        else:
            print(f"Failed to connect, return code {rc}\n", flush=True)
    # Set Connecting Client ID
    #client = mqtt_client.Client(client_id)

    # For paho-mqtt 2.0.0, you need to set callback_api_version.
    client = mqtt_client.Client(client_id=client_id,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
            clean_session=False)

    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(broker, port, keepalive=20) # TODO
    return client




def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):

        try:
            payload = msg.payload.decode()
            data = json.loads(payload)
        except Exception as e:
            print("Error decodificando JSON:", e, flush=True)
            return

        print(f"Mensaje recibido en {msg.topic}: {data}", flush=True)

        valorhr = int(data["hr"])
        valortemp = float(data["temp"])
        valorspo2 = int(data["SpO2"])
        valorresp = int(data["resp"])

 
        # ---- HR ----
        if valorhr > HR_MEDIO*1.10: # más de 10% sobre el valor medio
            client.publish(topic_alerts, json.dumps({
                "Métrica": "hr",
                "Valor": valorhr,
                "Alerta": "HR anómala"
            }), qos=1)
            print(f"ALERTA! HR anómala: {valorhr} BPM", flush=True)
        
        # ---- TEMP ----
        if valortemp > TEMP_LIMITE:
            client.publish(topic_alerts,json.dumps({
                "Métrica": "temp",
                "Valor": valortemp,
                "Alerta": "TEMP anómala"
            }), qos=1)
            print(f"ALERTA! TEMP anómala: {valortemp} ºC", flush=True)

        # ---- SPO2 ----
        if valorspo2 < SPO2_LIMITE:
            client.publish(topic_alerts, json.dumps({
                "Métrica": "SpO2",
                "Valor": valorspo2,
                "Alerta": "SPO2 anómala"
            }), qos=1)
            print(f"ALERTA! SPO2 anómala: {valorspo2} %", flush=True)

        # ---- RESP ----
        if valorresp < RESP_INF  or RESP_SUP < valorresp :
            client.publish(topic_alerts, json.dumps({
                "Métrica": "resp",
                "Valor": valorresp,
                "Alerta": "RESP anómala"
            }), qos=1)
            print(f"ALERTA! RESP anómala: {valorresp} BPM", flush=True)

    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    run()
