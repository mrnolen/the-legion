import streamlit as st
import os
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- SECURITY GATE ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Security Clearance Required", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password was incorrect, show input again.
        st.text_input(
            "Access Denied. Try Again", type="password", on_change=password_entered, key="password"
        )
        return False
    else:
        # Password was correct.
        return True

if check_password():
    # --- MAIN APP ---
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    pc = Pinecone(api_key=st.secrets["PINECONE_API_KEY"])
    index_name = st.secrets["PINECONE_INDEX_NAME"]
    index = pc.Index(index_name)

    st.title("⚔️ THE LEGION - SECURE")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter command..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        query_embedding = client.embeddings.create(
            input=prompt,
            model="text-embedding-3-small"
        ).data[0].embedding

        search_results = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True
        )

        context_text = ""
        for match in search_results["matches"]:
            context_text += match["metadata"]["text"] + "\n\n"

        system_prompt = f"""
        You are 'The Legion,' an elite strategic advisor.
        Answer strictly based on the context below.
        
        CONTEXT:
        {context_text}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        ai_response = response.choices[0].message.content
        
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
    