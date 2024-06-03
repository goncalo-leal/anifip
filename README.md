
# ANIFIP (Ad-Hoc Network Integration for Immersive Performances) 
Ad-Hoc Network Integration for Immersive Performances (ANIFIP) leverages the potential of adhoc networks through a range of inventive applications.
Our objective is to synchronize audio, visual effects, and lighting, culminating in immersive and captivating experiences for both performers and audiences.

ANIFIP is a project comprising two modules: a controller and a worker. The controller module, implemented in `sender.py`, is responsible for sending MIDI files and **bArtHoc** messages via MQTT to worker nodes. The worker module, implemented in `receiver.py`, receives MIDI files and performs synchronized actions on connected actuators. 
## Controller Module (`sender.py`)
 The controller module utilizes the MQTT protocol to communicate with the receiver module.
  It performs the following tasks:
  - Loads a MIDI file.
  -  Publishes the MIDI file to the receiver.
  -  Waits for acknowledgment from the receiver.
  -  Starts threads for reading MIDI messages and waiting for acknowledgment.
  -  Publishes **bArtHoc** messages depending on MIDI messages received from an input port. 
  - Controls playback.
## Worker Module (`receiver.py`)
 The worker module listens for incoming MIDI files over MQTT, controls playback, and actuates connected hardware.
 It performs the following tasks:
  - Listens for incoming MIDI files over MQTT.
  - Listens for **bArtHoc** messages to synchronize with other nodes.
  -  Actuates connected hardware.
## Dependencies 
All dependencies are listed in `requirements.txt`.
## Usage 
 1. Ensure that the dependencies are installed.
 2. Run the Worker module (`receiver.py`) on devices where actuators (e.g., audio, lighting) are connected.
  3. Run the Controller module (`sender.py`) on the device from which you want to send MIDI files, control playback, and read MIDI messages. 
  4. Plug the MIDI controller into the device running the Controller module. 
## Configuration 
Modify the configurations in the `config.py` file as per your requirements.
### Controller Device Follow these steps to configure the controller device:
#### Configure NTP
  1. Install NTP: `sudo apt-get update && sudo apt-get install ntp`.
   2. Edit NTP configuration: `sudo nano /etc/ntp.conf`, comment out other pool and server lines, and add `server 127.127.1.0` and `fudge 127.127.1.0 stratum 10`. 
   3. Synchronize clocks: `ntpq -p`.
#### Configure B.A.T.M.A.N
 1. Install `batman-adv`.
 2. Run `cd Desktop && ./batman_script.sh X`, replacing X with the ID of your Controller device.
#### Configure IPFS 
 1. Install `kubo-go`.
 2.  Initialize and run IPFS: `ipfs init` and `ipfs daemon`.
#### Launch sender.py
 1. Navigate to the sender directory: `cd sender`.
 2. Run `python sender.py`.
### Worker Device
Follow these steps to configure the worker device:
#### Configure NTP 
 1. Install NTP: `sudo apt-get update && sudo apt-get install ntp`.
 2. Edit NTP configuration: `sudo nano /etc/ntp.conf`, add `server 10.1.1.X` (replace X with the ID of the Controller device), and restart NTP service: `sudo systemctl restart ntp`.
 3. Synchronize clocks: `ntpq -p`.
#### Configure B.A.T.M.A.N
 1. Install `batman-adv`.
 2. Run `cd Desktop && ./batman_script.sh X`, replacing X with the ID of your Controller device.
 3.  Configure IPFS
 4.  No IPFS configuration is needed for worker nodes.
#### Launch receiver.py 
  1. Navigate to the receiver directory: `cd receiver`.
  2. Run `python receiver.py` for the receiver instance handling LED.
  3.  Run `python receiver_pc.py` for the receiver instance handling audio playback.
   4. Run `python receiver_visualizer.py` for the receiver instance displaying the Tkinter canvas based on the MIDI file.
