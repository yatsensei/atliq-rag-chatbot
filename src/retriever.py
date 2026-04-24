import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "atliq_docs")

def get_retriever(user_roles: list[str]):
    """
    Creates a retriever that only fetches documents the user is allowed to see.
    """
    # 1. Load the modern HuggingFace embedding model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 2. Connect to our local Qdrant database
    client = QdrantClient(url=QDRANT_URL)
    
    # 3. Use the modern QdrantVectorStore
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )

    # 4. Build the Role-Based Access Control (RBAC) Filter
    rbac_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.role",
                match=models.MatchAny(any=user_roles),
            )
        ]
    )

    # 5. Return the filtered retriever
    return vector_store.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": rbac_filter
        }
    )