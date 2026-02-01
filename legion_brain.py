import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

# 1. INITIALIZE
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

def search_memory(query):
    """Finds top 3 relevant strategic documents"""
    response = client.embeddings.create(input=query, model="text-embedding-3-small")
    results = index.query(
        namespace="strategic_doctrine", 
        vector=response.data[0].embedding, 
        top_k=3, 
        include_metadata=True
    )
    # Extract the text from the results
    memories = [match['metadata']['content'] for match in results['matches']]
    return "\n\n".join(memories)

def ask_legion(query):
    print(f"\n[Commander]: {query}")
    print(" [i] Scanning Neural Network for strategies...")
    
    # A. GET CONTEXT
    context = search_memory(query)
    
    if not context:
        print(" [!] No internal data found. Using general knowledge.")
        context = "No specific internal data available."
    
    # B. BUILD THE PROMPT
    # This tells GPT to use YOUR data as the source of truth
    system_prompt = f"""
    You are 'The Legion', an elite Real Estate Strategy AI.
    Use the provided STRATEGIC CONTEXT to answer the user's question.
    
    STRATEGIC CONTEXT:
    {context}
    
    RULES:
    1. If the answer is in the Context, use it and cite the numbers.
    2. Be concise, professional, and authoritative.
    3. Do not mention "context" or "documents" to the user. Just answer.
    """
    
    # C. GENERATE ANSWER
    response = client.chat.completions.create(
        model="gpt-4o", # Using the smartest model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    
    answer = response.choices[0].message.content
    print(f"\n[LEGION]: {answer}\n")
    print("-" * 50)

if __name__ == "__main__":
    print("--- LEGION ONLINE ---")
    while True:
        user_input = input("Enter Command (or 'exit'): ")
        if user_input.lower() in ['exit', 'quit']:
            break
        ask_legion(user_input)