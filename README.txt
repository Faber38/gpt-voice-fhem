# GPT Sprachsystem VM – Notizen & Setup

## 🎙 Mikrofon (Anker PowerConf S3)

- USB-Gerät wird dynamisch erkannt durch:
  /opt/script/find_s3_audio.sh

- Ergebnis wird gespeichert in:
  /opt/script/audio_device.conf

- Beispiel-Nutzung:
  DEVICE=$(cat /opt/script/audio_device.conf)
  arecord -D "$DEVICE" -f S16_LE -c1 -r 16000 -d 5 test.wav

- Wird beim Boot automatisch ausgeführt:
  systemd-Service: find-s3-audio.service

## 🎙 Mikrofon (Anker PowerConf S3)

Das Mikrofon "PowerConf S3" wird bei jedem Systemstart automatisch erkannt.

🛠️ Das Bash-Skript `/opt/script/find_s3_audio.sh` sucht anhand des Namens ("PowerConf S3") in der `arecord -l` Ausgabe das aktuelle ALSA-Gerät und speichert das Ergebnis als `plughw:<card>,<device>` in folgender Datei:

    /opt/script/audio_device.conf

📦 Beispielinhalt der Datei:
    plughw:1,0

⚙️ Das Skript wird beim Boot automatisch über den systemd-Dienst gestartet:

    systemctl status find-s3-audio.service

🧪 Verwendung in Sprachsystemen:
```bash
DEVICE=$(cat /opt/script/audio_device.conf)
arecord -D "$DEVICE" -f S16_LE -c1 -r 16000 -d 5 test.wav

## ⚡ GPU Passthrough & CUDA (RTX 3060)

### PCI-Geräte:
- GPU: 01:00.0 → [10de:2504]
- Audio: 02:00.0 → [10de:228e]

### Konfiguration:
- /etc/pve/qemu-server/210.conf:
    hostpci0: 01:00.0,pcie=1
    hostpci1: 02:00.0,pcie=1

- /etc/default/grub:
    GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_iommu=on iommu=pt"
    → danach: update-grub + reboot

- /etc/modules-load.d/vfio.conf:
    vfio
    vfio_iommu_type1
    vfio_pci
    vfio_virqfd

- /etc/modprobe.d/vfio.conf:
    options vfio-pci ids=10de:2504,10de:228e

- NVIDIA-Treiber via:
    ./cuda_12.3.1_545.23.08_linux.run

- Test nach Reboot:
    nvidia-smi
    lspci -k | grep -A 2 NVIDIA


## 🧠 Geplant:
- CUDA + llama.cpp für GPT
- Vosk/Whisper für Spracheingabe
- Coqui TTS oder ähnliches für Sprachausgabe
