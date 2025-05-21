import streamlit as st
import requests

import os
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("Gen-AI Document Assistant")

tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload", "❓ Ask", "💬 Chat", "🧾 Themes"])

# --- UPLOAD ---
with tab1:
    st.subheader("Upload a PDF")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{API_URL}/upload/", files=files)

        if response.status_code == 200:
            st.success("File uploaded successfully")
            st.json(response.json())
        else:
            st.error(f"Upload failed: {response.json()['error']}")

# --- QUERY ---
with tab2:
    st.subheader("Ask a question")
    question = st.text_input("Type your question...")

    if st.button("Submit Question") and question:
        response = requests.get(f"{API_URL}/query/", params={"query": question})
        if response.status_code == 200:
            data = response.json()
            for res in data["results"]:
                st.markdown(f"**📄 {res['filename']}**")
                st.write(res["answer"])
                st.caption(f"Chunk: {res['chunk_index']}")
        else:
            st.error(response.json()["error"])

# --- CHAT ---
with tab3:
    st.subheader("Document Chat")
    chat_history = st.session_state.get("chat_history", [])
    user_input = st.text_input("You:", key="chat_input")

    if st.button("Send"):
        history_text = [item for sublist in chat_history for item in sublist]
        payload = {"query": user_input, "history": history_text}

        response = requests.post(f"{API_URL}/chat/", json=payload)
        if response.status_code == 200:
            answer = response.json()["answer"]
            sources = response.json()["sources"]
            st.markdown(f"**Bot:** {answer}")
            st.caption(f"📄 Sources: {', '.join(sources)}")
            chat_history.append((user_input, answer))
            st.session_state["chat_history"] = chat_history
        else:
            st.error(response.json()["error"])

with tab4:
    st.subheader("🧾 Generate Themes from Documents")
    theme_query = st.text_input("Ask a high-level question (e.g. 'What are the compliance issues?')")

    if st.button("Generate Themes") and theme_query:
        response = requests.get(f"{API_URL}/themes/", params={"query": theme_query})
        if response.status_code == 200:
            data = response.json()
            for theme in data["themes"]:
                st.markdown(f"### {theme['title']}")
                st.write(theme["summary"])
                st.caption(f"📄 Supported by: {', '.join(theme['documents'])}")
        else:
            st.error(response.json()["error"])

