import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# 1. Load your environment variables
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "atliq_docs")
DATA_DIR = "data"

def main():
    print("Starting the ingestion process...")

    print("Loading embedding model (this might take a few seconds)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 3. Connect to the local Qdrant Vector Database
    client = QdrantClient(url=QDRANT_URL)

    # FIX: Manually wipe and recreate the collection using the native client
    if client.collection_exists(COLLECTION_NAME):
        print(f"\nWiping existing collection '{COLLECTION_NAME}' to prevent duplicates...")
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    print(f"Created fresh Qdrant collection: {COLLECTION_NAME}")

    # 4. Set up the Text Splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
    )

    all_splits = []

    # 5. Walk through our data folders
    for role_folder in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, role_folder)
        
        if not os.path.isdir(folder_path):
            continue
            
        print(f"\nProcessing department: {role_folder}")
        
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                
                loader = TextLoader(file_path)
                docs = loader.load()
                
                splits = text_splitter.split_documents(docs)
                
                # 6. Apply RBAC Metadata
                for i, split in enumerate(splits):
                    split.metadata["role"] = [role_folder]
                    split.metadata["source"] = filename
                    split.metadata["chunk_id"] = i
                    
                all_splits.extend(splits)
                print(f"  - Chopped '{filename}' into {len(splits)} pieces.")

    # 7. Store everything into Qdrant using the safer add_documents method
    print(f"\nEmbedding {len(all_splits)} total chunks and sending to Qdrant...")
    
    # Initialize the LangChain Qdrant wrapper with our existing client
    vector_store = Qdrant(
        client=client, 
        collection_name=COLLECTION_NAME, 
        embeddings=embeddings
    )
    
    # Add the documents safely
    vector_store.add_documents(all_splits)
    
    print("\nIngestion complete! AtliQ Corp data is now vectorized.")

if __name__ == "__main__":
    main()