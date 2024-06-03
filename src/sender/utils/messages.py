"""
This file will have the structure for each message that can be sent by the sender
"""

import json
import time
import uuid
from utils import ipfs_functions
import ntplib
from time import ctime
from utils import config

ntp_server = "localhost"

sent_messages = {}

def get_ntp_time(server):
    try:
        c = ntplib.NTPClient()
        response = c.request(server, version=3)
        return response.tx_time
    except Exception as e:
        print("Error fetching NTP time: %s", e)
        return None


def create_message(msg_type, action = None,data = None ,sqc_number = None, slave_id=None, slave_type=None, control_type=None):
    msg = None
    match msg_type:
        case "BROADCAST_DATA":
            msg = broadcast_data_msg(data)
        case "ACTION": 
            msg = action_msg(action, slave_type)
        case "BROADCAST_CONTROL":
            match control_type:
                case "CHANGE_MUSIC":
                    msg = broadcast_change_music_msg(control_type, data)
                case _:
                    msg = broadcast_control_msg(control_type)
        case "ACK":
            msg = ack_msg(slave_id, sqc_number)
    
    return msg



def broadcast_data_msg(data):

    uid = str(uuid.uuid4())
    ntp_time = get_ntp_time(ntp_server)
    data_cid = ipfs_functions.upload_file(data)

    msg = {"type" : "BROADCAST_DATA",
           "sequence_number" : uid,
           "timestamp": ntp_time    ,
           "data": data_cid
    }

    sent_messages[uid] = [msg,config.MQTT_NR_OF_NODES]

    return msg
    

def action_msg(action, slave_type):

    uid = str(uuid.uuid4())
    ntp_time = get_ntp_time(ntp_server)
    msg = {"type" : "ACTION",
           "sequence_number" : uid,
           "timestamp": ntp_time,
           "action": action,
           "slave_type": slave_type
    }

    sent_messages[uid] = [msg,config.MQTT_NR_OF_NODES]

    return msg


def broadcast_control_msg(control_type):
    uid = str(uuid.uuid4())
    ntp_time = get_ntp_time(ntp_server)
    start_time = ntp_time + 3  # Add 3 seconds to the NTP time

    msg = {"type": "BROADCAST_CONTROL",
           "sequence_number": uid,
           "timestamp": ntp_time,
           "start_timestamp": start_time,
           "control": control_type
    }

    sent_messages[uid] = [msg,config.MQTT_NR_OF_NODES]

    return msg


def broadcast_change_music_msg(control_type, data):

    uid = str(uuid.uuid4())
    ntp_time = get_ntp_time(ntp_server)
    msg = {"type": "BROADCAST_CONTROL",
           "sequence_number": uid,
           "timestamp": ntp_time,
           "control": control_type,
           "data": data
    }

    sent_messages[uid] = [msg, config.MQTT_NR_OF_NODES]
    
    return msg


def ack_msg(slave_id, sqc_number):

    uid = str(uuid.uuid4())
    ntp_time = get_ntp_time(ntp_server)
    msg = {"type": "ACK",
           "sequence_number": sqc_number,
           "timestamp": ntp_time,
           "slave_id" : slave_id
           }
    
    return msg


#this function will receive the message and check if it is an ack message and if it is the correct ack message
def ack_checker(message):
    ret = False
    if message.get("type") == "ACK":
        if message.get("sequence_number") in sent_messages.keys():
            if len(sent_messages[message.get("sequence_number")]) == 2:
                sent_messages[message.get("sequence_number")].append(set())
            
            sent_messages[message.get("sequence_number")][2].add(message.get("slave_id"))

            if len(sent_messages[message.get("sequence_number")][2]) == config.MQTT_NR_OF_NODES:
                ret = True
                del sent_messages[message.get("sequence_number")]
    return ret
        