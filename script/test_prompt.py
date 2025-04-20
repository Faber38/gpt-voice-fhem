from llama_cpp import Llama

# Modell laden (du kannst n_threads und n_gpu_layers anpassen)
llm = Llama(model_path="/opt/tinyllama.Q4_K_M.gguf", n_ctx=2048, n_threads=8)

prompt = "Antworte ausschließlich auf Deutsch.\nGib drei Wörter: Küche Licht aus\nAntwort:"
response = llm(prompt, max_tokens=10)

print("Antwort:", response["choices"][0]["text"].strip())
