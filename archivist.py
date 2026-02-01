import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

# 1. LOAD THE WEAPONS
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

def inject_wisdom(text, category):
    """
    Takes a business lesson, turns it into a Vector (Numbers), 
    and saves it to the Pinecone Temple forever.
    """
    print(f"--- INJECTING: {category} ---")
    
    # A. Turn Text into Soul (Vector)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    vector = response.data[0].embedding
    
    # B. Save to Pinecone
    # We use a random ID for now, but in production we'd use listing_id
    import uuid
    memory_id = str(uuid.uuid4())
    
    index.upsert(
        vectors=[(memory_id, vector, {"content": text, "category": category})],
        namespace="strategic_doctrine"
    )
    print(f" > SUCCESS: Memory stored under ID: {memory_id[:8]}...")

def ask_the_oracle(query):
    """
    Asks the Temple a question. It finds the most relevant past memories.
    """
    print(f"\n--- ASKING THE ORACLE: '{query}' ---")
    
    # A. Turn Question into Soul (Vector)
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    query_vector = response.data[0].embedding
    
    # B. Search the Temple
    results = index.query(
        namespace="strategic_doctrine",
        vector=query_vector,
        top_k=3, # Bring back the top 3 best answers
        include_metadata=True
    )
    
    # C. Reveal the Answer
    if not results['matches']:
        print(" > THE ORACLE IS SILENT (No memories found).")
    else:
        for match in results['matches']:
            score = match['score']
            wisdom = match['metadata']['content']
            print(f" > [Confidence: {int(score*100)}%] FOUND: {wisdom}")

# --- THE COMMAND CENTER ---
# This part runs when you start the script.

if __name__ == "__main__":
    
    print("Welcome, Commander. Choose your action:")
    print("1. TEACH (Inject new wisdom)")
    print("2. ASK (Consult the memories)")
    
    choice = input("Type 1 or 2: ")
    
    if choice == "1":
        lesson = input("Enter the wisdom to store (e.g., 'Heated pools increase occupancy by 20%'): ")
        category = input("Enter category (e.g., 'Revenue'): ")
        inject_wisdom(lesson, category)
        
    elif choice == "2":
        question = input("What do you wish to know? ")
        ask_the_oracle(question)