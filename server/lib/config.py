import os
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), "../vector_db")
OPENAI_MODEL = "gpt-5"
OPENAI_EMBEDDINGS_MODEL = "text-embedding-3-large"
COLLECTION_NAME = "eora_info"
HOST = "::" #change to 0.0.0.0 if on local
