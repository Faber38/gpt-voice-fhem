#!/usr/bin/env python3
import time
import sys
import os
from llama_cpp import Llama
from contextlib import redirect_stdout, redirect_stderr
import io

MODEL_PATH = "/opt/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
PROMPT = "Die Temperatur im Wohnzimmer beträgt 21 Komma 9 Grad Celsius. Formuliere eine freundliche Antwort."

def run_model(n_gpu_layers, silent=True):
    print(f"\n🚀 Starte Benchmark mit {n_gpu_layers} GPU-Layern ...")
    start_total = time.time()

    if silent:
        f_null = io.StringIO()
        with redirect_stdout(f_null), redirect_stderr(f_null):
            llm = Llama(
                model_path=MODEL_PATH,
                n_gpu_layers=n_gpu_layers,
                n_ctx=2048,
                use_mlock=True,
                use_mmap=True
            )
    else:
        llm = Llama(
            model_path=MODEL_PATH,
            n_gpu_layers=n_gpu_layers,
            n_ctx=2048,
            use_mlock=True,
            use_mmap=True
        )

    print("✅ Modell geladen.")
    start = time.time()
    output = llm(PROMPT, max_tokens=100, stop=["\n"])
    duration = time.time() - start
    total_duration = time.time() - start_total

    antwort = output["choices"][0]["text"].strip()
    print(f"🧠 Antwort: {antwort}")
    print(f"⌛ Antwortzeit: {duration:.2f} Sekunden")
    print(f"⏱️ Gesamtdauer inkl. Modell-Init: {total_duration:.2f} Sekunden")

if __name__ == "__main__":
    run_model(n_gpu_layers=0, silent=True)    # 🔵 CPU
    run_model(n_gpu_layers=35, silent=True)   # 🟢 GPU

