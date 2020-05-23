import flowlib.units._rfid as rfid
import flowlib.hats._speaker as speaker
from utime import sleep
from machine import Pin
from simple import MQTTClient
import network
import ubinascii
import machine
import ujson as json
GROVE_PINS = [32,33]

last_uid = ""

lf_result = False
lf_id = ""
lf_master = False

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

def handle_reg(reader, mqtt):
    speaker.tone(200, 1000)
    while True:
        if reader.isCardOn():
            new_card = reader.readUid()
            break
    obj = dict()
    obj["type"] = "register"
    obj["card"] = new_card
    mqtt.publish("rfidauth", json.dumps(obj))

def handle_sub(topic,msg):
    global lf_result
    global lf_id
    global lf_master
    obj = json.loads(msg)
    if obj["type"] == "authresp":
        if obj["result"] == "failed":
            lf_result = False
        else:
            lf_result = True
        lf_id = obj["for"]
    else:
        if obj["type"] == "master":
            lf_result = True
            lf_master = True
        





wlan = network.WLAN(network.STA_IF)
wlan.active(1)
wlan.connect("TP-Link_MAIN", "TlPE707*37387!")

while not wlan.isconnected():
    print("not_connected")



mqtt_ip = "192.168.0.122"
mqtt_to = "rfidauth"
mqtt_from = "rfidauth_r"

mclient = MQTTClient(CLIENT_ID, mqtt_ip)
mclient.connect()
mclient.set_callback(handle_sub)
mclient.subscribe(mqtt_from)




reader = rfid.Rfid(GROVE_PINS)
speaker = speaker.Speaker()


while True:
    print(reader.isCardOn())
    while reader.isCardOn():
        uid = reader.readUid()
        if uid == "" or uid == " ":
            break
        if uid == last_uid:
            speaker.tone(200,800)
            break
        last_uid = uid
        obj = dict()
        obj["type"] = "auth"
        obj["card"] = uid
        mclient.publish(mqtt_to, json.dumps(obj))
        mclient.wait_msg()
        while lf_id != uid:
            print(lf_id)
            print(uid)
            mclient.wait_msg()
        if lf_result:
            speaker.tone(350, 500)
        else:
            speaker.tone(500, 1500)
        if lf_master:
            lf_master = False
            handle_reg(reader, mclient)
        sleep(0.3)
