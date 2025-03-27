from fastapi import FastAPI, HTTPException, Request
# Import AsyncElasticsearch instead of Elasticsearch
from elasticsearch import AsyncElasticsearch, exceptions as es_exceptions
import time
import logging
import os

# ... (logging setup remains the same) ...
# --->>> ADD OR UNCOMMENT THESE LINES <<<---
# Configure logging format and level
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Get the logger for the current module
logger = logging.getLogger(__name__)
# --->>> END OF LINES TO CHECK/ADD <<<


app = FastAPI()

ES_HOST = os.getenv("ELASTICSEARCH_HOSTS", "http://elasticsearch:9200")
INDEX_NAME = "wikipedia_india"

es_client = None # Will hold the AsyncElasticsearch client instance

@app.on_event("startup")
async def startup_event():
    global es_client
    retries = 5
    delay = 10
    for i in range(retries):
        try:
            # Instantiate AsyncElasticsearch
            es_client = AsyncElasticsearch(hosts=[ES_HOST])

            # Ping is also awaitable now
            if not await es_client.ping():
                raise ConnectionError("Elasticsearch ping failed")
            logger.info(f"Successfully connected to Elasticsearch at {ES_HOST}")

            await initialize_index_and_data()
            break

        # Make sure to catch appropriate exceptions
        except (es_exceptions.ConnectionError, ConnectionError, Exception) as e:
            logger.warning(f"Elasticsearch connection failed (Attempt {i+1}/{retries}): {e}. Retrying in {delay} seconds...")
            time.sleep(delay) # time.sleep is blocking, consider asyncio.sleep if strict async needed here
    else:
        logger.error(f"Could not connect to Elasticsearch after {retries} attempts. Exiting.")
        es_client = None

# async def initialize_index_and_data():
#     if not es_client:
#         logger.error("Elasticsearch client not initialized. Cannot setup index.")
#         return

#     try:
#         # --- Correct usage with await ---
#         if not await es_client.indices.exists(index=INDEX_NAME):
#             logger.info(f"Index '{INDEX_NAME}' not found. Creating index...")
#             index_settings = {
#                 "mappings": {
#                     "properties": {
#                         "id": {"type": "keyword"},
#                         "text": {"type": "text"}
#                     }
#                 }
#             }
#             # --- Correct usage with await ---
#             await es_client.indices.create(index=INDEX_NAME, body=index_settings)
#             logger.info(f"Index '{INDEX_NAME}' created.")

#             docs = [
#                 # ... (your docs remain the same) ...
#                  {"id": "para1", "text": "India, officially the Republic of India (ISO: Bhārat Gaṇarājya), is a country in South Asia. It is the seventh-largest country by area; the most populous country as of June 2023; and from the time of its independence in 1947, the world's most populous democracy."},
#                  {"id": "para2", "text": "Bounded by the Indian Ocean on the south, the Arabian Sea on the southwest, and the Bay of Bengal on the southeast, it shares land borders with Pakistan to the west; China, Nepal, and Bhutan to the north; and Bangladesh and Myanmar to the east. In the Indian Ocean, India is in the vicinity of Sri Lanka and the Maldives; its Andaman and Nicobar Islands share a maritime border with Thailand, Myanmar, and Indonesia."},
#                  {"id": "para3", "text": "Modern humans arrived on the Indian subcontinent from Africa no later than 55,000 years ago. Their long occupation, initially in varying forms of isolation as hunter-gatherers, has made the region highly diverse, second only to Africa in human genetic diversity."},
#                  {"id": "para4", "text": "Settled life emerged on the subcontinent in the western margins of the Indus river basin approximately 9,000 years ago, evolving gradually into the Indus Valley Civilisation of the third millennium BCE. By 1200 BCE, an archaic form of Sanskrit, an Indo-European language, had diffused into India from the northwest."}
#             ]

#             logger.info(f"Inserting {len(docs)} initial documents...")
#             for i, doc_body in enumerate(docs):
#                 try:
#                      # --- Correct usage with await ---
#                     await es_client.index(index=INDEX_NAME, id=doc_body['id'], document=doc_body)
#                     logger.info(f"Document {doc_body['id']} indexed.")
#                 # Handle potential indexing errors per document
#                 except es_exceptions.RequestError as req_err:
#                      logger.error(f"Error indexing document {doc_body['id']}: {req_err.info['error']['reason']}")
#                 except Exception as e:
#                      logger.error(f"Unexpected error indexing document {doc_body['id']}: {e}")
#             logger.info("Initial data population complete.")
#         else:
#             logger.info(f"Index '{INDEX_NAME}' already exists. Skipping creation and initial data population.")

#     # Catch errors specifically for index operations
#     except es_exceptions.ConnectionError:
#          logger.error("Connection failed during index initialization.")
#     except es_exceptions.RequestError as req_err:
#          logger.error(f"Elasticsearch request error during index setup: {req_err.info}")
#     except Exception as e:
#          logger.error(f"An unexpected error occurred during index setup: {e}")

async def initialize_index_and_data():
    # ... (error handling for client not initialized) ...
    try:
        # --- Check if index exists ---
        # Uses the AsyncElasticsearch client correctly with await
        if not await es_client.indices.exists(index=INDEX_NAME):
            logger.info(f"Index '{INDEX_NAME}' not found. Creating index...")

            # --- Define index mapping ---
            index_settings = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"}, # As required
                        "text": {"type": "text"}    # As required
                    }
                }
            }
            # --- Create the index ---
            await es_client.indices.create(index=INDEX_NAME, body=index_settings)
            logger.info(f"Index '{INDEX_NAME}' created.")

            # --- Define the 4 documents ---
            docs = [
                 {"id": "para1", "text": "India, officially the Republic of India (ISO: Bhārat Gaṇarājya), is a country in South Asia. It is the seventh-largest country by area; the most populous country as of June 2023; and from the time of its independence in 1947, the world's most populous democracy."},
                 {"id": "para2", "text": "Bounded by the Indian Ocean on the south, the Arabian Sea on the southwest, and the Bay of Bengal on the southeast, it shares land borders with Pakistan to the west; China, Nepal, and Bhutan to the north; and Bangladesh and Myanmar to the east. In the Indian Ocean, India is in the vicinity of Sri Lanka and the Maldives; its Andaman and Nicobar Islands share a maritime border with Thailand, Myanmar, and Indonesia."},
                 {"id": "para3", "text": "Modern humans arrived on the Indian subcontinent from Africa no later than 55,000 years ago. Their long occupation, initially in varying forms of isolation as hunter-gatherers, has made the region highly diverse, second only to Africa in human genetic diversity."},
                 {"id": "para4", "text": "Settled life emerged on the subcontinent in the western margins of the Indus river basin approximately 9,000 years ago, evolving gradually into the Indus Valley Civilisation of the third millennium BCE. By 1200 BCE, an archaic form of Sanskrit, an Indo-European language, had diffused into India from the northwest."}
            ]

            logger.info(f"Inserting {len(docs)} initial documents...")
            # --- Loop and insert each document with its specified ID ---
            for doc_body in docs:
                try:
                    # Use the 'id' field from the dictionary as the document ID in Elasticsearch
                    await es_client.index(index=INDEX_NAME, id=doc_body['id'], document=doc_body)
                    logger.info(f"Document {doc_body['id']} indexed.")
                except es_exceptions.RequestError as req_err:
                     logger.error(f"Error indexing document {doc_body['id']}: {req_err.info['error']['reason']}")
                except Exception as e:
                     logger.error(f"Unexpected error indexing document {doc_body['id']}: {e}")
            logger.info("Initial data population complete.")

        else:
            # --- If index already exists ---
            logger.info(f"Index '{INDEX_NAME}' already exists. Skipping creation and initial data population.")

    except es_exceptions.ConnectionError:
            logger.error("Connection failed during index initialization.")
        


@app.post("/search")
async def search_documents(request: Request):
    # --- Ensure ping is awaited ---
    if not es_client or not await es_client.ping():
         raise HTTPException(status_code=503, detail="Elasticsearch service unavailable")
    try:
        data = await request.json()
        query_text = data.get("query")
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing 'query' in request body")

        logger.info(f"Received search query: {query_text}")
        search_body = {"query": {"match": {"text": query_text}}}

        # --- Correct usage with await ---
        res = await es_client.search(index=INDEX_NAME, body=search_body)

        hits = res['hits']['hits']
        if hits:
            best_hit = hits[0]
            logger.info(f"Best match found: ID={best_hit['_id']}, Score={best_hit['_score']}")
            return {"id": best_hit['_id'], "text": best_hit['_source']['text'], "score": best_hit['_score']}
        else:
            logger.info("No documents found matching the query.")
            # It's better to return a 200 OK with an empty result or message
            # than a 404 if the *index* exists but no *documents* match.
            # Let's keep the original 404 mapping for now as it matches the symptom
            # but consider changing this in a real app.
            return {"message": "No documents found"} # Return this instead of raising 404

    except es_exceptions.NotFoundError:
         # This occurs if the INDEX itself doesn't exist
         logger.warning(f"Search failed because index '{INDEX_NAME}' not found.")
         raise HTTPException(status_code=404, detail=f"Index '{INDEX_NAME}' not found. Backend setup might have failed.")
    except es_exceptions.RequestError as req_err:
         logger.error(f"Elasticsearch request error during search: {req_err.info}")
         raise HTTPException(status_code=500, detail=f"Search error: {req_err.info['error']['reason']}")
    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during search")


@app.post("/insert")
async def insert_document(request: Request):
     # --- Ensure ping is awaited ---
    if not es_client or not await es_client.ping():
         raise HTTPException(status_code=503, detail="Elasticsearch service unavailable")
    try:
        data = await request.json()
        doc_text = data.get("text")
        if not doc_text:
            raise HTTPException(status_code=400, detail="Missing 'text' in request body")

        doc_body = {"text": doc_text}
        logger.info(f"Received request to insert document.")

        # --- Correct usage with await ---
        res = await es_client.index(index=INDEX_NAME, document=doc_body)

        logger.info(f"Document inserted successfully with ID: {res['_id']}")
        # Ensure the response object structure is correct before accessing '_id'
        doc_id = res.get('_id', 'N/A') # Safer access
        return {"message": "Document inserted successfully", "id": doc_id}

    except es_exceptions.NotFoundError:
         logger.warning(f"Insert failed because index '{INDEX_NAME}' not found.")
         raise HTTPException(status_code=404, detail=f"Index '{INDEX_NAME}' not found. Backend setup might have failed.")
    except es_exceptions.RequestError as req_err:
         logger.error(f"Elasticsearch request error during insert: {req_err.info}")
         raise HTTPException(status_code=500, detail=f"Insert error: {req_err.info['error']['reason']}")
    except Exception as e:
        logger.error(f"Error during insert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during insert")

@app.get("/")
def read_root():
    return {"message": "Backend is running"}

# --- main execution part (uvicorn command in Dockerfile handles this) ---
# No changes needed here