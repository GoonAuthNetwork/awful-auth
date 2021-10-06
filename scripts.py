import json
import uvicorn

from app.main import app


def start():
    """Launches the application via uvicorn"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


def generate_openapi():
    """Generates openapi.json for the application"""
    with open("openapi.json", "w") as outfile:
        json.dump(app.openapi(), outfile)
