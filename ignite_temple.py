import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec

# 1. EQUIP THE SHIELD (Load Keys)
load_dotenv()
print("\n--- INITIATING TEMPLE PROTOCOL ---")

# 2. AWAKEN THE BRAIN (OpenAI)
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(" [X] ERROR: OpenAI Key is missing from .env file!")
        exit()
    client = OpenAI(api_key=api_key)
    print(" [v] THE BRAIN IS ONLINE (OpenAI Connected)")
except Exception as e:
    print(f" [X] THE BRAIN IS DEAD: {e}")
    exit()

# 3. AWAKEN THE MEMORY (Pinecone)
try:
    pc_key = os.getenv("PINECONE_API_KEY")
    if not pc_key:
        print(" [X] ERROR: Pinecone Key is missing from .env file!")
        exit()
        
    pc = Pinecone(api_key=pc_key)
    index_name = "master-vision-legacy"
    
    # Check if we can talk to Pinecone
    print(f" [i] Connecting to Pinecone...")
    existing_indexes = [i.name for i in pc.list_indexes()]
    print(f" [v] THE MEMORY IS ONLINE. Existing Indexes: {existing_indexes}")

    # Create the Index if it doesn't exist
    if index_name not in existing_indexes:
        print(f" [!] Constructing new Altar '{index_name}'...")
        try:
            pc.create_index(
                name=index_name,
                dimension=1536, 
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            print(" [v] ALTAR CONSTRUCTED SUCCESSFULLY.")
        except Exception as create_error:
            print(f" [!] Could not auto-create index (Free Tier limit?): {create_error}")
            print(" [i] Skipping creation, assuming index exists or will be created manually.")

except Exception as e:
    print(f" [X] THE MEMORY IS UNREACHABLE: {e}")
    exit()

print("\n--- TEMPLE VERIFICATION COMPLETE ---")