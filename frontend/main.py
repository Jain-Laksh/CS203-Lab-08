from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests # To communicate with the backend service
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# --- Backend Service Configuration ---
# The frontend needs to talk to the backend service over the Docker network
# Use the backend service name defined in docker-compose.yml
BACKEND_SERVICE_URL = os.getenv("BACKEND_URL", "http://1:9567") # Port 9567 is where backend listens internally


# --- Root Endpoint to Serve HTML ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main HTML page."""
    logger.info("Serving index.html")
    return templates.TemplateResponse("index.html", {"request": request})


# --- Endpoint to Proxy Search Request to Backend ---
@app.post("/get_best_match")
async def get_best_match(request: Request):
    """Receives search query from browser, forwards to backend, returns result."""
    try:
        data = await request.json()
        query = data.get("query")
        logger.info(f"Frontend received search request for: {query}")

        # Forward the request to the backend service
        backend_search_url = f"{BACKEND_SERVICE_URL}/search"
        response = requests.post(backend_search_url, json={"query": query})
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        logger.info(f"Frontend received backend response: {response.status_code}")
        return response.json()

    except requests.exceptions.RequestException as e:
         logger.error(f"Error communicating with backend service at {backend_search_url}: {e}")
         raise HTTPException(status_code=503, detail=f"Backend service unavailable: {e}")
    except Exception as e:
        logger.error(f"Error processing get_best_match request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error in frontend proxy")


# --- Endpoint to Proxy Insert Request to Backend ---
@app.post("/insert_document")
async def insert_document(request: Request):
    """Receives insert data from browser, forwards to backend, returns result."""
    try:
        data = await request.json()
        text = data.get("text")
        logger.info(f"Frontend received insert request.")

         # Forward the request to the backend service
        backend_insert_url = f"{BACKEND_SERVICE_URL}/insert"
        response = requests.post(backend_insert_url, json={"text": text})
        response.raise_for_status() # Raise HTTPError for bad responses

        logger.info(f"Frontend received backend insert response: {response.status_code}")
        return response.json()

    except requests.exceptions.RequestException as e:
         logger.error(f"Error communicating with backend service at {backend_insert_url}: {e}")
         raise HTTPException(status_code=503, detail=f"Backend service unavailable: {e}")
    except Exception as e:
        logger.error(f"Error processing insert_document request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error in frontend proxy")

# Note