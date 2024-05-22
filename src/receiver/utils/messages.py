"""
This file will have the structure for each message that can be sent by the receiver
"""

import json
import time
import uuid
from utils import ipfs_functions
from utils import config
from utils import midi
import ntplib


def create_ack_message(sqc_number = None, slave_id=None):
    msg = ack_msg(slave_id, sqc_number)
    
    return msg


def get_ntp_time(server_address):
    c = ntplib.NTPClient()
    response = c.request(server_address)
    return response.tx_time - 2208988800  # Convert from NTP to Unix timestamp


def ack_msg(slave_id, sqc_number):

    uid = str(uuid.uuid4())

    msg = {"type": "ACK",
           "sequence_number": sqc_number,
           "timestamp": time.time(),
           "slave_id" : slave_id
           }
    
    return msg


def process(message):
    msg_type = message.get("type")
    ack_msg = None

    match msg_type:
        case "BROADCAST_DATA":
            #get data from ipfs
            data_cid = message.get("data")
            res = ipfs_functions.download_file(data_cid, f"midi_files/{config.MIDI_FILE}")
            
            if res:
                ack_msg = create_ack_message(message.get("sequence_number"), config.SLAVE_ID)
                print ("MIDI file received")
                return ack_msg,None
            else:
                return None
        case "ACTION":
            slave_type = message.get("slave_type")

            if config.SLAVE_TYPE  == slave_type:
                midi.set_current_action(message.get("action"))
                print("current")

            ack_msg = create_ack_message(message.get("sequence_number"),config.SLAVE_ID)
            print("ignorado")
            return ack_msg,None 
        
        case "BROADCAST_CONTROL":
            control_type = message.get("control_type")
            match control_type:
                case _:
                   #sender address in this case is on 
                   # Extract the timestamp from the message
                    timestamp = message.get("start_timestamp")
                    if timestamp:
                        current_time = time.time()  # Replace 'sender_ip_address' with the actual IP
			
                        delay = (timestamp - current_time)
                        if delay >= 0:
                            print(f"Delaying execution for {delay} seconds to synchronize")
                            # After delay, acknowledge synchronization
                        ack_msg = create_ack_message(message.get("sequence_number"), config.SLAVE_ID)
                        return ack_msg,delay
        case "ACK":
            print("ACK")
