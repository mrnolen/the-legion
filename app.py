
# Version 2.0 - Secure
import streamlit as st
import os
import uuid
import pypdf
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

# 1. SETUP & CONFIG
load_dotenv()
st.set_page_config(page_title="The Legion", page_icon="⚔️", layout="wide")

try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
except Exception as e:
    st.error(f"SYSTEM ERROR: Check your .env file. {e}")
    st.stop()

# --- INTERNAL FUNCTIONS ---

def add_memory(text, filename):
    """Chunks text and saves it to Pinecone."""
    try:
        # Create Embedding
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        vector = response.data[0].embedding
        
        # Save to Cloud
        memory_id = str(uuid.uuid4())
        index.upsert(
            vectors=[(memory_id, vector, {"content": text, "source": filename})],
            namespace="strategic_doctrine"
        )
        return True
    except Exception as e:
        st.error(f"Upload Failed: {e}")
        return False

def get_strategic_answer(query):
    """Finds relevant docs and asks GPT-4."""
    # Search Pinecone
    emb_response = client.embeddings.create(input=query, model="text-embedding-3-small")
    search_results = index.query(
        namespace="strategic_doctrine", 
        vector=emb_response.data[0].embedding, 
        top_k=5, 
        include_metadata=True
    )
    
    # Compile Context
    context_text = "\n\n".join([m['metadata']['content'] for m in search_results['matches']])
    if not context_text: context_text = "No specific internal protocols found."

    # Prompt GPT
    system_prompt = f"""
    You are 'The Legion'. 
    Your mission is to answer the user's question using the provided STRATEGIC CONTEXT.
    
    RULES:
    1. You must answer based on the Context provided below.
    2. Do not filter information. If the answer is in the Context, reveal it.
    3. Be direct and concise.
    
    STRATEGIC CONTEXT:
    {context_text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content

def read_pdf(file):
    reader = pypdf.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# --- THE USER INTERFACE ---

# SIDEBAR: The Training Deck
with st.sidebar:
    st.header("📂 Training Deck")
    st.write("Upload strategy docs (PDF or TXT).")
    
    uploaded_file = st.file_uploader("Upload File", type=["txt", "pdf"])
    
    if uploaded_file is not None:
        if st.button("Inject Wisdom"):
            with st.spinner("Assimilating Data..."):
                # 1. Extract Text
                if uploaded_file.name.endswith(".pdf"):
                    raw_text = read_pdf(uploaded_file)
                else:
                    raw_text = uploaded_file.getvalue().decode("utf-8")
                
                # 2. Chunk and Save
                # We split by paragraphs to avoid sending massive blocks
                paragraphs = raw_text.split('\n\n')
                
                count = 0
                progress_bar = st.progress(0)
                
                for i, para in enumerate(paragraphs):
                    if len(para.strip()) > 20: # Ignore tiny lines
                        add_memory(para.strip(), uploaded_file.name)
                        count += 1
                    # Update bar safely
                    if len(paragraphs) > 0:
                        progress_bar.progress(min((i + 1) / len(paragraphs), 1.0))
                
                st.success(f"✅ Success! {count} strategic blocks stored.")

# MAIN PANEL: The War Room
st.title("⚔️ THE LEGION")
st.markdown("### Interactive Strategy Command")
st.divider()

# Chat Input
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask for strategy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing Database..."):
            response = get_strategic_answer(prompt)
            st.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})