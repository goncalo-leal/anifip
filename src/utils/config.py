"""
Configuration file for the sender module
"""

# Logging
LOG_FILE = "sender.log"

# MIDI
MIDI_FILE = "Vivaldi Winter (Allegro).mid"
MIDI_CHUNK_SIZE = 256
MIDI_PORT = "Midi Through:Midi Through Port-0 14:0"

# MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# Topics
TOPIC_MIDI = "midi"
TOPIC_SERVICE_DISCOVERY = "service_discovery"

# MIDI Thresholds
BASS_THRESHOLD = 55
TREBLE_THRESHOLD = 70

#Raspberry Pi
LED_PIN = 17