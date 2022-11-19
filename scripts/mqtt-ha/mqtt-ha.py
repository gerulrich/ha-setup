#!/usr/bin/env python
# required packages:
# apt-get install python3-paho-mqtt python3-dotenv

import paho.mqtt.client as mqtt
import json
import os
import logging
from dotenv import load_dotenv
load_dotenv()

script_dir = os.getenv("SCRIPT_DIR")
# TODO sacar mediante servicio rest
client = mqtt.Client("mqtt-ha")
devices = {
  "redmi7a": "192.168.0.141",
  "redmi_note4": "192.168.0.155",
  "google_tv": "192.168.0.209",
  "xbox": "192.168.1.112",
  "mac_book_pro": "192.168.0.168"
}

def on_camera_message(payload):
    os.system(f'{script_dir}/security_cam.sh')
    result = {
        "chatId": payload["chatId"],
        "content": "/tmp/camera/webcam.jpeg"
    }
    logging.info("Sending image path to topic '/camera/snapshot/output'")
    client.publish("/camera/snapshot/output", json.dumps(result))

def on_firewall_message(payload):
    device=payload["device"]
    if payload["status"] == "on":
        logging.info(f'Enable internet on {device} device with ip {devices[device]}')
        os.system(f'{script_dir}/enable_internet.sh {devices[device]}')
    else:
        logging.info(f'Disable internet on {device} device with ip {devices[device]}')
        os.system(f'{script_dir}/disable_internet.sh {devices[device]}')
        client.publish("/firewall/forward/result", "ok")

def on_wifi_message(payload):
    logging.info("Reiniciando wifi")
    os.system("f'{script_dir}/restart_wifi.sh")
    client.publish("/wifi/radio0/result", "ok")

def on_message(mclient, userdata, message):
    payload = json.loads(str(message.payload.decode("utf-8","ignore")))
    match message.topic:
        case "/camera/snapshot":
            on_camera_message(payload)
        case "/firewall/forward":
            on_firewall_message(payload)
        case "/wifi/radio0":
            on_wifi_message(payload)
        case _:
            logging.warn(f'Topic {message.topic} not handled')


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    try:
        mqtt_host = os.getenv("MQTT_HOST")
        mqtt_user = os.getenv("MQTT_USER")
        mqtt_pass = os.getenv("MQTT_PASS")

        client.username_pw_set(mqtt_user, mqtt_pass)
        client.connect(mqtt_host)
        client.subscribe("/camera/foto/action")
        client.subscribe("/internet/access")
        client.subscribe("/wifi/radio0")
        client.on_message=on_message
        client.loop_forever()
    except:
        logging.error("failed to connect, moving on")