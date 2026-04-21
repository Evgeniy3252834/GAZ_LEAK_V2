#!/usr/bin/env python
"""Проверка импортов всех модулей"""

import sys

print(f"Python version: {sys.version}")
print("\nChecking imports...")

modules = [
    ("torch", "PyTorch"),
    ("torchvision", "TorchVision"),
    ("cv2", "OpenCV"),
    ("PIL", "Pillow"),
    ("numpy", "NumPy"),
    ("dotenv", "python-dotenv"),
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("pytest", "Pytest"),
    ("sqlite3", "SQLite3 (built-in)"),
]

success = True
for module, name in modules:
    try:
        if module == "sqlite3":
            import sqlite3
        else:
            __import__(module)
        print(f"✓ {name} - OK")
    except ImportError as e:
        print(f"✗ {name} - FAILED: {e}")
        success = False

if success:
    print("\n✅ All imports successful!")
else:
    print("\n❌ Some imports failed. Please install missing packages.")
    sys.exit(1)
