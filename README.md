# 🚀 Document Research & Theme Identification Chatbot

This project outlines the complete step-by-step implementation of the Document Research & Theme Identification Chatbot project — from document ingestion to semantic search and theme summarization, including Dockerization.

---

##  Step 1: Project Setup

**Backend:**
- Structure created inside `/backend/app`
- Used `FastAPI`, `SQLAlchemy`, `pytesseract`, `pdfplumber` for OCR
- Initialized SQLite database using SQLAlchemy ORM

**Frontend:**
- Built with **Streamlit**
- Used `requests` to interact with FastAPI backend

---

##  Step 2: Document Upload

- Endpoint: `POST /upload/`
- Uploads PDFs via FastAPI and stores them in `/backend/data/uploads/`
- Extracts text using `pytesseract` (OCR)
- Saves extracted content in the `Document` table of SQLite

---

##  Step 3: Text Chunking & Embedding

- Text is chunked using `langchain.text_splitter.RecursiveCharacterTextSplitter`
- Embeddings generated using `sentence-transformers` (`all-MiniLM-L6-v2`)
- Stored in **ChromaDB** with metadata (doc ID, filename, chunk index)

---

##  Step 4: Semantic Search

- Endpoint: `GET /query/`
- Accepts user questions
- Queries the ChromaDB vector store using embedded query
- Returns top document chunks + metadata (doc ID, chunk index)

---

##  Step 5: Verify Embedding Storage

- Checked with `collection.count()` to ensure chunks were stored
- Verified queries return results for embedded documents

---

##  Step 6: Theme Summarization

- Built `/theme/` endpoint
- Uses HuggingFace BART (`facebook/bart-large-cnn`)
- Summarizes grouped document chunks into readable themes

---

##  Step 7: Frontend Integration

- UI for uploading documents, running queries, and getting themes
- Connected backend endpoints via Streamlit interface
- Displayed search results and summarized theme(s) in the browser

---

##  Step 8: Optional Enhancements

- [x] Duplicate file detection on upload
- [x] Delete documents via API (`DELETE /delete/{id}`)
- [ ] Export theme summaries to file (optional)
- [ ] Multi-theme extraction support (planned)

---

##  Step 9: Dockerization

- Added `Dockerfile` for both backend and frontend
- Created `docker-compose.yml` for running both services together
- Issues solved:
  - Switched to HuggingFace embeddings to avoid OpenAI quota limits
  - Replaced `chromadb` PyPI version with direct clone (if needed)
  - Installed Rust and `protoc` for compiling dependencies

---


