import paho.mqtt.client as mqtt
import json
import time

cards = dict()
cards["3ccef4bd"] = "Pokol kártya"
authentications = []

def on_con(client,userdata,flags,rc):
    print("Connection to MQTT Server acquired")
    client.subscribe("rfidauth")
    
def on_msg(client,userdata,msg):
    print(str(msg.payload))
    obj = json.loads(msg.payload)
    
    if obj["type"] == "auth":
        if obj["card"] in cards.keys():
            retobj = dict()
            retobj["type"] = "authresp"
            retobj["for"] = obj["card"]
            retobj["result"] = "success"
            client.publish("rfidauth_r", json.dumps(retobj))
            print("sent resp")
        else:
            retobj = dict()
            retobj["type"] = "authresp"
            retobj["for"] = obj["card"]
            retobj["result"] = "failed"
            client.publish("rfidauth_r", json.dumps(retobj))
            print("sent resp")
           
client = mqtt.Client()

client.on_connect = on_con
client.on_message = on_msg

client.connect("192.168.0.122", 1883)

client.loop_forever()