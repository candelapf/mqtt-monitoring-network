# 🩺 Clinical IoT Telemetry & Remote Patient Monitoring System

Plataforma de telemetría médica y monitorización de pacientes en tiempo real diseñada para la transmisión, detección de anomalías y visualización de bioseñales críticas sobre redes IP virtualizadas. Proyecto desarrollado en la asignatura **Redes y Servicios** (Grado en Ingeniería Biomédica, ETSIT - Universidad Politécnica de Madrid).

El sistema integra la emulación de constantes fisiológicas, la segmentación y enrutamiento estático mediante routers virtuales bajo **VNX / LXC**, la intermediación mediante un broker **MQTT (EMQX)** y cuadro de mando en **Grafana** desplegados en contenedores **Docker**, y la auditoría del tráfico de red a nivel de paquetes con **Wireshark**.

---

## 🌟 Arquitectura del Escenario

El entorno modela un flujo de telemedicina donde el dispositivo del paciente (`h2`) y el puesto de control/alertas (`h3`) se encuentran en subredes aisladas interconectadas por dos routers intermedios (`r1`, `r2`) y conectados al host central:

```text
 [ Dispositivo Paciente ]
           (h2)
       10.1.0.2/24
            |
            | (Net0: 10.1.0.0/24)
            |
       10.1.0.1/24 (eth1)
        [ Router r1 ]
       10.1.1.1/24 (eth2)
            |
            | (Net1: 10.1.1.0/24)
            |
       10.1.1.2/24 (eth1)
        [ Router r2 ]
       10.1.2.1/24 (eth2)
            |
            | (Net2: 10.1.2.0/24)
            |
       10.1.2.2/24 (eth1)
           (h3)
 [ Suscriptor / Alertas ]

            +--- Router r1 (eth3: Interfaz hacia Host)
            | (Net3: Host Bridge / Docker Network)
     [ Host Central ]
     ├── EMQX Broker MQTT (Puertos 1883, 8083, 18083)
     └── Servidor Grafana + MQTT Datasource (Puerto 3000)
```

---

## 🛠️ Tecnologías y Protocolos

* **Protocolos de Comunicación:** MQTT v5.0/v3.1.1 (negociación `CONNECT`/`CONNACK`, niveles de calidad de servicio `QoS 0` y `QoS 1`, mensajes de control *Keep-Alive*), TCP/IP.
* **Broker MQTT:** [EMQX](https://www.emqx.io/) v5.0.2 desplegado en contenedor Docker.
* **Visualización de Series Temporales:** [Grafana Enterprise](https://grafana.com/) con el plugin `grafana-mqtt-datasource`.
* **Emulación de Red e Infraestructura:** [VNX](https://dit.upm.es/vnx/) (Virtual Networks over LinuX) con escenarios XML y contenedores LXC.
* **Lenguajes y Herramientas:** Python 3 (`paho-mqtt`), Bash scripting, Wireshark / TShark.

---

## 📂 Estructura del Repositorio

```text
mqtt-monitoring-network/
├── .gitignore                  # Exclusión de binarios y temporales
├── README.md                   # Documentación y guía de despliegue
│
├── src/                        # Lógica de aplicación en Python
│   ├── client.py               # Publicador MQTT de métricas fisiológicas
│   ├── subs.py                 # Suscriptor y motor de detección de anomalías
│   └── utils.py                # Funciones auxiliares y serialización JSON
│
├── network/                    # Configuración del entorno de red virtual
│   ├── vnx-integracion.xml     # Definición del escenario multi-router en VNX
│   ├── install.sh              # Script de despliegue automático de la red
│   └── dependencies.sh         # Instalación de librerías en los nodos
│
├── data/                       # Generación y emulación de bioseñales
│   ├── Human_vital_signs_R.csv # Registro clínico base (FC, FR, SpO2, Temp)
│   └── reporter.sh             # Script de muestreo continuo hacia report.csv
│
└── captures/                   # Trazas de tráfico para análisis en Wireshark
    ├── captura_final.pcapng    # Flujo global del sistema integrado
    ├── qos0.pcapng             # Análisis de entrega no garantizada (QoS 0)
    ├── qos1.pcapng             # Análisis de entrega confirmada con PUBACK (QoS 1)
    └── alertas.pcapng          # Segmentación del tráfico de alarmas críticas
```

---

## 🚀 Guía de Despliegue y Puesta en Marcha

### 1. Despliegue de los Servicios Centrales en el Host
En la máquina host (o máquina virtual principal), arranca las instancias Docker del broker EMQX y Grafana:

```bash
# 1. Arrancar el broker EMQX
sudo docker run -d --name emqx \
  -p 1883:1883 -p 8083:8083 -p 8883:8883 -p 8084:8084 -p 18083:18083 \
  emqx/emqx:5.0.2

# 2. Arrancar Grafana con el plugin de MQTT instalado
sudo docker run -d -p 3000:3000 --name grafana \
  -e "GF_INSTALL_PLUGINS=grafana-mqtt-datasource" \
  grafana/grafana-enterprise
```

Para obtener la dirección IP asignada al broker dentro de la red del host/Docker, ejecuta:
```bash
sudo docker inspect $(sudo docker ps | grep emqx | awk '{print $1}') | grep "IPAddress"
```

---

### 2. Arranque del Escenario de Red Virtualizada (VNX)
Navega al directorio `network/` e inicia el escenario:
```bash
cd network
chmod +x install.sh dependencies.sh
sudo ./install.sh
```
*El proceso inicializa los routers virtuales `r1` y `r2`, junto con los nodos cliente `h2` y `h3`.*

---

### 3. Configuración de Enrutamiento IP

Accede a la consola de cada dispositivo para fijar el direccionamiento y configurar las tablas de reenvío IP hacia el broker (asumiendo que el broker reside en la subred `172.17.0.0/16` del host):

* **En el dispositivo del paciente (`h2`):**
  ```bash
  ip address add 10.1.0.2/24 dev eth1
  ip route add default via 10.1.0.1
  ```

* **En el router `r1`:**
  ```bash
  ip address add 10.1.0.1/24 dev eth1
  ip address add 10.1.1.1/24 dev eth2
  ip route add 10.1.2.0/24 via 10.1.1.2
  sysctl -w net.ipv4.ip_forward=1
  ```

* **En el router `r2`:**
  ```bash
  ip address add 10.1.1.2/24 dev eth1
  ip address add 10.1.2.1/24 dev eth2
  ip route add default via 10.1.1.1
  sysctl -w net.ipv4.ip_forward=1
  ```

* **En el puesto de alertas (`h3`):**
  ```bash
  ip address add 10.1.2.2/24 dev eth1
  ip route add default via 10.1.2.1
  ```

> *Verifica la conectividad entre extremos ejecutando `ping 10.1.2.2` desde `h2` y haciendo ping a la IP del broker.*

---

### 4. Ejecución del Flujo de Monitorización

#### Paso A: Arrancar el suscriptor y detector de alertas (`h3`)
Desde la consola del nodo `h3`:
```bash
python3 src/subs.py
```
*El nodo queda a la escucha del tópico MQTT correspondiente, analizando cada lectura y disparando advertencias si se detectan valores fuera de los límites fisiológicos seguros.*

#### Paso B: Iniciar la captura de constantes y publicación (`h2`)
Desde la consola del nodo `h2`:
```bash
# Iniciar la emulación de bioseñales en segundo plano
./data/reporter.sh &

# Arrancar el publicador MQTT
python3 src/client.py
```
*El script lee progresivamente los datos de `report.csv`, los formatea en JSON y los publica periódicamente al broker EMQX.*

---

### 5. Cuadro de Mando en Grafana

1. Abre tu navegador web en `http://localhost:3000` (credenciales por defecto: `admin` / `admin`).
2. Añade un nuevo **Data Source** seleccionando **MQTT**.
3. Configura la URL del broker (`tcp://<IP_BROKER>:1883`) y define el tópico de escucha.
4. Construye paneles de series temporales para visualizar en vivo la evolución de la frecuencia cardíaca, saturación de oxígeno ($SpO_2$) y temperatura.

---

## 🔍 Análisis y Auditoría de Tráfico (Wireshark)

En el directorio `captures/` se incluyen las trazas de paquetes `.pcapng` obtenidas en las interfaces de red para validar el comportamiento del protocolo:
* **`qos0.pcapng` vs `qos1.pcapng`:** Demostración del mecanismo de entrega no confirmada frente a la entrega con acuse de recibo (`PUBACK`).
* **`alertas.pcapng`:** Captura del intercambio de mensajes desencadenados ante eventos clínicos anómalos.
* **`captura_final.pcapng`:** Flujo completo de extremo a extremo atravesando los múltiples saltos de enrutamiento IP.
