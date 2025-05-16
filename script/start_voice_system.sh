#!/bin/bash

# 🔁 Pfade
VENV_PYTHON="/opt/venv/bin/python"
SCRIPT_DIR="/opt/script"
WAKEWORD="$SCRIPT_DIR/wakeword.py"
AUDIO_SCRIPT="$SCRIPT_DIR/find_audio_devices.py"

if [ -z "$1" ]; then
    echo "⚙️ Verwendung: $0 {start|stop|restart|status}"
    exit 1
fi

# 🔍 Funktionen
start_services() {
    echo "🚀 Starte Sprachsystem …"

    echo "🔍 Finde Audio-Geräte …"
    $VENV_PYTHON $AUDIO_SCRIPT
    if [[ $? -ne 0 ]]; then
        echo "❌ Fehler beim Finden der Audio-Geräte."
        exit 1
    fi

    if pgrep -fx "$VENV_PYTHON $WAKEWORD" > /dev/null; then
        echo "⚠️ Wakeword-Listener läuft bereits."
    else
        echo "🎧 Starte Wakeword Listener …"
        $VENV_PYTHON $WAKEWORD || {
            echo "❌ Wakeword-Listener ist abgestürzt."
            exit 2
        }
    fi
}

stop_services() {
    echo "🛑 Beende Sprachsystem …"
    pkill -fx "$VENV_PYTHON $WAKEWORD" && echo "🧹 Wakeword gestoppt."
}

status_services() {
    echo "📊 Status:"
    pgrep -af "$WAKEWORD" || echo "❌ Wakeword nicht aktiv"
}

# 🧠 Argumentverarbeitung
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 1
        start_services
        ;;
    status)
        status_services
        ;;
    *)
        echo "⚙️ Verwendung: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
