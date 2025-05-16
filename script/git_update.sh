#!/bin/bash

# Wechsle ins Projektverzeichnis
cd /opt || exit

# Prüfen, ob /opt ein Git-Repo ist
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "/opt ist kein Git-Repository!"
  exit 1
fi

# Git Status anzeigen
git status

# Prüfen, ob Änderungen vorliegen
if [[ -n $(git status --porcelain) ]]; then
  echo "Es gibt Änderungen zum Commit."

  # Commit-Nachricht abfragen
  read -rp "Bitte Commit-Nachricht eingeben: " commit_message
  if [[ -z "$commit_message" ]]; then
    echo "Fehlende Commit-Nachricht – Vorgang abgebrochen."
    exit 1
  fi

  # Änderungen hinzufügen und committen
  git add .
  git commit -m "$commit_message"
  echo -e "\n✅ Commit erstellt:"

  # Letzten Commit anzeigen
  git log -1 --oneline --graph --decorate

  # Optional: Rückfrage zum Push
  read -rp "Push an origin durchführen? (j/n): " confirm
  if [[ "$confirm" == "j" ]]; then
    git push
    echo -e "\n🚀 Push erfolgreich. Letzter Commit:"
    git log -1 --oneline --graph --decorate
  else
    echo "Push abgebrochen."
  fi
else
  echo "Keine Änderungen gefunden. Nichts zu tun."
fi
