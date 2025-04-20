🛠️ INSTALLATION (EN)
Requirements

    Linux (tested on Debian/Proxmox)

    Python 3.11+ (recommend using venv)

    sounddevice, vosk, samplerate, numpy, requests

    Vosk German model (vosk-model-small-de-0.15)

    ALSA-compatible USB microphone (e.g. Anker PowerConf S3)

    Local FHEM instance with dummy GptVoiceCommand

🔧 Step-by-step Setup
1. Clone the repository

git clone https://github.com/Faber38/gpt-voice-fhem.git
cd gpt-voice-fhem

2. Create virtual environment

python3 -m venv /opt/venv
source /opt/venv/bin/activate
pip install -r requirements.txt

3. Prepare directories

mkdir -p /opt/sound/responses /opt/sound/confirm /opt/sound/error
mkdir -p /opt/vosk

4. Add sample files (optional)

Place example WAVs (e.g. ich_höre.wav, klar,mach_ich.wav) in the corresponding folders.
5. Vosk model

Download and unzip the Vosk model:

wget https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip -P /opt/vosk
unzip /opt/vosk/vosk-model-small-de-0.15.zip -d /opt/vosk/

6. Audio device configuration

Detect the device index:

python /opt/script/find_audio_index.py

Save it in:

/opt/script/audio_index.conf

Optional: configure aplay device in /opt/script/audio_device.conf, e.g.:

hw:CARD=S3,DEV=0

7. FHEM Configuration

Add gpt.conf to your FHEM fhem.cfg. It contains the logic for executing commands via GptVoiceCommand.

You must also create a file /opt/script/fhem_auth.conf:

[FHEM]
url = http://192.168.x.x:8083
user = holger
pass = deinpasswort

Make sure the file has proper permissions (e.g. chmod 600).
▶️ Start manually

/opt/venv/bin/python /opt/script/wakeword_niko.py

🚀 Autostart (systemd)

Create a systemd unit (e.g. /etc/systemd/system/gpt-voice.service):

[Unit]
Description=GPT Voice Wakeword
After=network.target

[Service]
ExecStart=/opt/venv/bin/python /opt/script/wakeword_niko.py
WorkingDirectory=/opt/
Restart=always
User=root

[Install]
WantedBy=multi-user.target

Enable it:

systemctl enable --now gpt-voice.service
