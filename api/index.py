import os
import sys
from pathlib import Path

# Ensure Backend directory is in Python path for Vercel Serverless Function imports
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "Backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

__all__ = ["app"]
