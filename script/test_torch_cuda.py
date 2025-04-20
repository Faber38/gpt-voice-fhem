#!/usr/bin/env python3
import torch

print("🧪 PyTorch Test")

# 🔢 Version anzeigen
print(f"📦 Version: {torch.__version__}")

# 💻 CUDA verfügbar?
if torch.cuda.is_available():
    device = torch.device("cuda")
    print(f"✅ CUDA ist verfügbar! Verwende: {torch.cuda.get_device_name(0)}")

    # 🔍 Mini-Tensor-Test auf der GPU
    a = torch.rand(3, 3, device=device)
    b = torch.rand(3, 3, device=device)
    c = a + b
    print("🚀 Tensor-Rechnung auf GPU erfolgreich!")
    print(c)

else:
    print("❌ CUDA ist NICHT verfügbar.")
