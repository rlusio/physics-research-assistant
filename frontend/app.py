
import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Physics Research Assistant",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Physics Research Assistant")
st.caption("Ask questions about your scientific documents.")

# Historia czatu przechowywana w bieżącej sesji Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []


# PANEL BOCZNY
with st.sidebar:
    st.header("Documents")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )

    if st.button("Process document", disabled=uploaded_file is None):
        with st.spinner("Processing PDF..."):
            try:
                response = requests.post(
                    f"{API_URL}/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    },
                    timeout=300
                )
                response.raise_for_status()

                result = response.json()

                st.success(
                    f"Indexed {result['pages']} pages "
                    f"and {result['chunks']} chunks."
                )

            except requests.RequestException as error:
                st.error(f"Upload failed: {error}")


# HISTORIA ROZMOWY
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# POLE PYTANIA
question = st.chat_input("Ask a question about your PDFs...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=300
                )
                response.raise_for_status()

                answer = response.json()["answer"]
                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except requests.RequestException as error:
                st.error(f"Request failed: {error}")
