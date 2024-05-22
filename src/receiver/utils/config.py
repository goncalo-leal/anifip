"""
Configuration file for the sender module
"""

# Logging
LOG_FILE = "sender.log"

# MIDI
MIDI_FILE = "file.mid"
MIDI_CHUNK_SIZE = 256
MIDI_PORT = "Midi Through:Midi Through Port-0 14:0"

# MQTT
MQTT_BROKER = "10.1.1.15"
MQTT_PORT = 1883

#SLAVE_INFO
SLAVE_TYPE = "LED"
SLAVE_ID = 1

# Topics
TOPIC_MASTER_OUT = "midi"
TOPIC_MASTER_IN = "ack"
TOPIC_SERVICE_DISCOVERY = "service_discovery"

# MIDI Thresholds
BASS_THRESHOLD = 55
TREBLE_THRESHOLD = 70

#Raspberry Pi
LED_PIN1 = 17
LED_PIN2 = 18

#Action
START_ACTION = "LED_BLINK_WITH_BASS"