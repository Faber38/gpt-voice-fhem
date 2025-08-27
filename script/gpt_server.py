# /opt/script/gpt_server.py

from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, shutil

app = FastAPI()
TMP_BASE = "/tmp"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/audio_upload")
async def upload_audio(request: Request, file: UploadFile = File(...)):
    client = request.query_params.get("client", "default")
    tmp_dir = f"{TMP_BASE}/{client}"
    send_path = os.path.join(tmp_dir, "sende.wav")
    response_path = os.path.join(tmp_dir, "response.wav")

    os.makedirs(tmp_dir, exist_ok=True)

 #   if os.path.exists(response_path):
 #       os.remove(response_path)
#        print(f"🧽 Alte Antwort gelöscht: {response_path}")

    with open(send_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    print(f"📥 Empfangen: {send_path}")

    try:
        from modules.commands_client import handle_client_audio
        handle_client_audio(client)
    except Exception as e:
        print(f"❌ Fehler bei Verarbeitung für '{client}': {e}")
        return {"error": str(e)}

    if os.path.exists(send_path):
        os.remove(send_path)
        print(f"🗑️ sende.wav gelöscht: {send_path}")

    return {"status": "received", "client": client}

@app.get("/client_audio/{client}")
async def get_audio(client: str):
    response_path = os.path.join(TMP_BASE, client, "response.wav")
    if os.path.exists(response_path):
        print(f"📤 Sende Antwort für '{client}'")
        return FileResponse(response_path, media_type="audio/wav", filename="response.wav")
    raise HTTPException(status_code=404, detail="Keine Antwortdatei vorhanden.")

@app.get("/client_meta/{client}")
async def get_meta(client: str):
    meta_path = os.path.join(TMP_BASE, client, "response_meta.json")
    if os.path.exists(meta_path):
        return FileResponse(meta_path, media_type="application/json", filename="response_meta.json")
    raise HTTPException(status_code=404, detail="Keine Meta-Datei vorhanden.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gpt_server:app", host="0.0.0.0", port=8000)
