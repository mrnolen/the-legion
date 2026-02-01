import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import time

# 1. LOAD WEAPONS
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

def embed_text(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def mass_upload(filename):
    print(f"--- OPENING THE VAULT: {filename} ---")
    
    with open(filename, "r") as f:
        lines = f.readlines()
        
    print(f" > FOUND {len(lines)} DATA POINTS. BEGINNING UPLOAD...")
    
    batch = []
    import uuid
    
    for line in lines:
        if line.strip(): # Skip empty lines
            vector = embed_text(line)
            memory_id = str(uuid.uuid4())
            metadata = {"content": line.strip(), "source": filename}
            
            # Add to batch
            batch.append((memory_id, vector, metadata))
            print(f"   > PROCESSED: {line[:30]}...")
            
    # Push to Pinecone
    index.upsert(vectors=batch, namespace="strategic_doctrine")
    print(f"\n [v] UPLOAD COMPLETE. {len(batch)} memories added to the Legion.")

if __name__ == "__main__":
    mass_upload("knowledge.txt")