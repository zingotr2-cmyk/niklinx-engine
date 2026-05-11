"""
WSGI entry point for production servers (gunicorn, uvicorn).
This file lives at project root so PYTHONPATH issues are eliminated.
Usage: gunicorn wsgi:app
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.routes_api import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
