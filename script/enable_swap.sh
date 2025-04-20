#!/bin/bash

SWAPFILE="/swapfile"
SIZE="32G"

echo "🔧 Erstelle Swap-Datei mit $SIZE ..."

# Prüfen ob Swap bereits existiert
if [ -f "$SWAPFILE" ]; then
    echo "⚠️  Swap-Datei existiert bereits: $SWAPFILE"
    exit 1
fi

# Swap-Datei erstellen und Berechtigungen setzen
fallocate -l $SIZE $SWAPFILE || dd if=/dev/zero of=$SWAPFILE bs=1M count=32768
chmod 600 $SWAPFILE
mkswap $SWAPFILE
swapon $SWAPFILE

# In /etc/fstab eintragen, damit es nach Reboot bleibt
echo "$SWAPFILE none swap sw 0 0" >> /etc/fstab

echo "✅ Swap aktiviert!"
swapon --show
free -h
