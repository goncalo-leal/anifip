"""
Configuration file for the sender module
"""

# Logging
LOG_FILE = "sender.log"

# MIDI
MIDI_FILE = "Vivaldi Winter (Allegro).mid"
MIDI_FILE2 = "midi2.mid"
MIDI_CHUNK_SIZE = 256
MIDI_PORT = "Midi Through:Midi Through Port-0 14:0"

# MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_NR_OF_NODES = 2

# Topics
TOPIC_MASTER_OUT = "midi"
TOPIC_MASTER_IN = "ack"
TOPIC_SERVICE_DISCOVERY = "service_discovery"

# MIDI Thresholds
BASS_THRESHOLD = 55
TREBLE_THRESHOLD = 70

#Raspberry Pi
LED_PIN = 17