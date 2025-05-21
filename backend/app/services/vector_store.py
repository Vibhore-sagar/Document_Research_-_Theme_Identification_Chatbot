import os
from dotenv import load_dotenv
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from app.models.document import Document
from typing import List

# Load env variables (optional, for future config)
load_dotenv()

# ✅ Initialize HuggingFace embedding model (free)
hf_model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Define embedding function for Chroma
class HuggingFaceEmbedder:
    def __call__(self, input: List[str]) -> List[List[float]]:
        return hf_model.encode(input).tolist()

embedding_function = HuggingFaceEmbedder()

# ✅ Set up ChromaDB client
chroma_client = chromadb.Client()

# ✅ Create collection with HuggingFace embedder
collection = chroma_client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_function
)

def split_and_store_chunks(document: Document):
    """Chunk the document and store embeddings in ChromaDB."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(document.content)

    if not chunks:
        print("⚠️ No chunks generated.")
        return

    ids = [f"{document.id}_{i}" for i in range(len(chunks))]
    metadatas = [{"doc_id": document.id, "chunk_index": i, "filename": document.filename} for i in range(len(chunks))]

    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ Stored {len(chunks)} chunks for document ID {document.id}")
    print(f"🧠 Total chunks now in collection: {collection.count()}")


def semantic_search(query: str, top_k: int = 5):
    """Perform a semantic search using local HuggingFace embeddings."""
    return collection.query(
        query_texts=[query],
        n_results=top_k
    )
