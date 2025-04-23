#!/bin/bash

# Verzeichnis deines Repos
cd /opt || exit

# Git Status anzeigen
git status

# Prüfen ob Änderungen vorliegen
if [[ -n $(git status --porcelain) ]]; then
  echo "Es gibt Änderungen zum Commit."
  
  # Commit-Nachricht abfragen
  read -p "Bitte Commit-Nachricht eingeben: " commit_message

  # Änderungen hinzufügen, committen und pushen
  git add .
  git commit -m "$commit_message"
  git push

  echo "Änderungen wurden erfolgreich gepusht."
else
  echo "Keine Änderungen gefunden. Nichts zu tun."
fi
