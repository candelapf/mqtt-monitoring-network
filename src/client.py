import time
import pandas as pd
import random
import time
from paho.mqtt import client as mqtt_client
from utils import read_report
from utils import line_to_json
from utils import line_to_dict
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
topic = 'rserG10/vitals'
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'
username = 'admin'
password = 'public'

def connect_mqtt():
    #def on_connect(client, userdata, flags, rc):
    def on_connect(client, userdata, flags, rc, properties):
    # For paho-mqtt 2.0.0, you need to add the properties parameter.
    # def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!", flush=True)
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





def publish(client):
    msg_count = 1


    #############################
    # VITAL SIGNS AUX VARIABLES #
    #############################
    # Fill here with necessary auxiliary variables
    # TODO
    
    tiempo_espera = (10 % 5) + 5

    # Inicializar índice de fila si no existe
    if not hasattr(publish, "row_index"):
        publish.row_index = 0  # primera línea a leer


    while True:
        #time.sleep(5)

        ######################
        ## READ VITAL SIGNS ##
        ######################

        print(FIRST_RECONNECT_DELAY, flush=True)
        # TODO
        # Pasamos de usar read_report() que lee líneas concretas a line_to_dict() para leer todo el csv.
        # line_to_dict() convierte una línea del csv en diccionario Python
        # line_to_json() convierte una línea a json para publicarlos en MQTT
        try:
            datadic = line_to_dict('report.csv', publish.row_index + 1)
            if datadic is None:
                print(f"Línea {publish.row_index+1} no válida, saltando...")
                publish.row_index += 1
                continue
        except Exception as e:
            print("ERROR al leer report.csv:", e, flush=True)
            datadic = []
        

        # TODO: missing code to keep track of last read line
        publish.row_index += 1

        datadic_en_json = json.dumps(datadic)
        msg = datadic_en_json

        result = client.publish(topic, msg, qos=1)
        print('result', flush=True)
        print(result, flush=True)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`", flush=True)
        else:
            print(f"Failed to send message to topic {topic}", flush=True)

        # topic_1 = client.publish('vitals/hr', str(datadic['hr']), qos=1)
        # print(f"Publicado hr: {datadic['hr']} en vitals/hr")
        # topic_2 = client.publish('vitals/resp', str(datadic['resp']), qos=1)
        # print(f"Publicado resp: {datadic['resp']} en vitals/resp")
        # topic_3 = client.publish('vitals/SpO2', str(datadic['SpO2']), qos=1)
        # print(f"Publicado SpO2: {datadic['SpO2']} en vitals/SpO2")
        # topic_4 = client.publish('vitals/temp', str(datadic['temp']), qos=1)
        # print(f"Publicado temp: {datadic['temp']} en vitals/temp")
        

        msg_count += 1
        time.sleep(tiempo_espera)


# def publish(client):
#     msg_count = 1


#     #############################
#     # VITAL SIGNS AUX VARIABLES #
#     #############################
#     # Fill here with necessary auxiliary variables
#     # TODO
#     tiempo_espera = (10 % 5) + 5

#     # Inicializar índice de fila si no existe
#     if not hasattr(publish, "row_index"):
#         publish.row_index = 0  # primera línea a leer


#     while True:
#         # time.sleep(5)

#         ######################
#         ## READ VITAL SIGNS ##
#         ######################

#         print(FIRST_RECONNECT_DELAY, flush=True)
#         # TODO: read next line(s) and store in "lines"

#         # Leer solo una línea (línea = row_index + 1 porque read_report empieza contando desde 1)
#         try:
#             linea_tal_cual = read_report('report.csv', publish.row_index + 1, 1)
#         except Exception as e:
#             print("ERROR al leer report.csv:", e, flush=True)
#             linea_tal_cual = []

#         if linea_tal_cual:  
#             # read_report devuelve una lista con UNA línea, la sacamos
#             linea = linea_tal_cual[0]
                        


#         # TODO: missing code to keep track of last read line
#         publish.row_index += 1


#         lines = ';'.join(linea)

#         mensaje_json = line_to_json(linea)


#         msg = f"messages: {msg_count}" # SOL
#         msg = mensaje_json
#         result = client.publish(topic, msg, qos=1)
#         print('result', flush=True)
#         print(result, flush=True)
#         status = result[0]
#         if status == 0:
#             print(f"Send `{msg}` to topic `{topic}`", flush=True)
#         else:
#             print(f"Failed to send message to topic {topic}", flush=True)
#         msg_count += 1
#         time.sleep(tiempo_espera)




def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()


if __name__ == '__main__':
    run()






