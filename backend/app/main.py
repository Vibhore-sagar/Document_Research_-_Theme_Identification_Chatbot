
from fastapi import FastAPI, UploadFile, File, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import os, shutil
from sqlalchemy.exc import IntegrityError
from .services.chat_engine import generate_answer
from pydantic import BaseModel
from fastapi import HTTPException
from .services.vector_store import collection  # already imported

# Import your internal modules
from .services.text_extraction import extract_text_from_pdf
from .core.database import SessionLocal, init_db
from .models.document import Document
from .services.vector_store import split_and_store_chunks, semantic_search, collection
from .services.theme_engine import synthesize_themes


# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Startup hook to initialize the database
@app.on_event("startup")
def startup_event():
    init_db()

# ✅ Root test route
@app.get("/")
def read_root():
    return {"message": "Wasserstoff Gen-AI Chatbot API is running"}

# ✅ Document upload endpoint
UPLOAD_DIR = "backend/data/uploads"

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extracted_text = extract_text_from_pdf(file_location)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to extract text: {str(e)}"}
        )

    db = SessionLocal()

    # Check for duplicate
    existing = db.query(Document).filter_by(filename=file.filename).first()
    if existing:
        db.close()
        return JSONResponse(
            status_code=409,
            content={"error": f"File '{file.filename}' already exists in the database."}
        )

    doc = Document(filename=file.filename, filepath=file_location, content=extracted_text)
    try:
        db.add(doc)
        db.commit()
        db.refresh(doc)
    except IntegrityError as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"error": f"Database Integrity Error: {str(e.orig)}"}
        )
    finally:
        db.close()

    try:
        split_and_store_chunks(doc)
        print(f"✅ ChromaDB count after upload: {collection.count()}")
    except Exception as embed_err:
        return JSONResponse(
            status_code=500,
            content={"error": f"Embedding error: {str(embed_err)}"}
        )

    return {
        "id": doc.id,
        "filename": doc.filename,
        "text_sample": extracted_text[:500]
    }

# ✅ Get all uploaded documents
@app.get("/documents/")
def list_documents():
    db = SessionLocal()
    docs = db.query(Document).all()
    db.close()
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "uploaded_at": doc.uploaded_at,
        }
        for doc in docs
    ]

# ✅ Query documents via semantic search
@app.get("/query/")
async def query_documents(query: str = Query(..., description="Your question")):
    try:
        results = semantic_search(query)
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        answers = []
        for i in range(len(documents)):
            answers.append({
                "answer": documents[i],
                "doc_id": metadatas[i]["doc_id"],
                "filename": metadatas[i]["filename"],
                "chunk_index": metadatas[i]["chunk_index"]
            })

        return {"query": query, "results": answers}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process query: {str(e)}"}
        )
@app.get("/themes/")
async def generate_themes(query: str = Query(..., description="Your question")):
    try:
        results = semantic_search(query)
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        themes = synthesize_themes(query, documents, metadatas)

        return {
            "query": query,
            "themes": themes
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate themes: {str(e)}"}
        )
    
class ChatRequest(BaseModel):
    query: str
    history: List[str]
@app.post("/chat/")
async def chat_with_documents(request: ChatRequest):
    try:
        results = semantic_search(request.query)
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        answer = generate_answer(request.query, request.history, documents)

        return {
            "query": request.query,
            "answer": answer,
            "sources": list({meta["filename"] for meta in metadatas})
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Chat failed: {str(e)}"}
        )


@app.delete("/delete/{doc_id}")
def delete_document(doc_id: int):
    db = SessionLocal()
    doc = db.query(Document).filter_by(id=doc_id).first()

    if not doc:
        db.close()
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete associated embeddings from ChromaDB
    num_chunks = 0
    try:
        chunk_ids = [f"{doc_id}_{i}" for i in range(1000)]  # up to 1000 chunks assumed
        collection.delete(ids=chunk_ids)
        num_chunks = len(chunk_ids)
    except Exception as e:
        print(f"⚠️ Failed to remove embeddings: {e}")

    # Delete file from filesystem
    try:
        if os.path.exists(doc.filepath):
            os.remove(doc.filepath)
    except Exception as e:
        print(f"⚠️ Failed to delete file: {e}")

    # Delete DB entry
    db.delete(doc)
    db.commit()
    db.close()

    return {
        "message": f"Document '{doc.filename}' deleted successfully.",
        "chunks_removed": num_chunks
    }


