"""
Entrypoint for the application
"""
import uvicorn
from src.api.server import app

if __name__ == "__main__":
    uvicorn.run(app)
