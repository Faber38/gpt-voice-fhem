# CUDA Upgrade (GPU Support)

## Geplante Hardware:
- NVIDIA RTX 3060 12GB

## Erwarteter Performance-Gewinn:
| Anwendung      | Aktuell (CPU) | Geplant (GPU) |
|----------------|---------------|---------------|
| Whisper.cpp    | 20-30 Sek     | 2-5 Sek       |
| GPT Antwort    | 5-10 Sek      | bleibt CPU    |

## ToDo nach Einbau:
- NVIDIA Treiber installieren
- whisper.cpp mit CUDA bauen
- whisper-server testen mit CUDA
- Benchmark Vergleich
