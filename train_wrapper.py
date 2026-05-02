#!/usr/bin/env python3
"""
Train Rasa with a workaround for Windows temporary directory permission issues.
"""
import os
import sys
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

# Patch shutil.rmtree to ignore permission errors
_original_rmtree = shutil.rmtree

def permissive_rmtree(path, ignore_errors=False, onerror=None):
    """rmtree wrapper that ignores permission errors during temp cleanup."""
    try:
        _original_rmtree(path, ignore_errors=True)
    except (PermissionError, OSError) as e:
        print(f"[INFO] Ignored cleanup error on {path}: {e}")
        pass

shutil.rmtree = permissive_rmtree

try:
    print("[INFO] Starting Rasa training with permission error handling...")
    from rasa.api import train
    
    model_path = train(
        domain="domain.yml",
        config="config.yml",
        training_files="data/",
        output="models/",
    )
    print(f"[INFO] Training completed! Model saved at: {model_path}")
except Exception as e:
    print(f"[ERROR] Training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
