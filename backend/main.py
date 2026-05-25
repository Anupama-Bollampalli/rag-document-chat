from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_engine import ingest_document, retrieve, list_documents
import llm as llm_module

app = FastAPI(
    title="RAG Document Chat API",
    description="Upload documents and chat with them using RAG. Compare LLM responses across temperature settings.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPERATURES = [0.0, 0.5, 1.0, 1.5]


class ChatRequest(BaseModel):
    query: str
    temperature: float = 0.7


class TempStudyRequest(BaseModel):
    query: str


@app.get("/")
def root():
    return {
        "name": "RAG Document Chat API",
        "version": "1.0.0",
        "status": "running",
        "llm": "groq" if llm_module._USE_GROQ else "mock",
        "docs": "/docs",
        "endpoints": ["/health", "/documents", "/upload", "/chat", "/temperature-study"],
    }


@app.get("/health")
def health():
    return {"status": "ok", "llm": "groq" if llm_module._USE_GROQ else "mock"}


@app.get("/documents")
def get_documents():
    return {"documents": list_documents()}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    is_pdf = file.filename.lower().endswith(".pdf")
    if not is_pdf and not file.filename.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files supported")
    result = ingest_document(file.filename, content, is_pdf)
    return {"message": f"Ingested {result['chunks']} chunks from {result['filename']}", **result}


@app.post("/chat")
def chat(req: ChatRequest):
    chunks = retrieve(req.query)
    if not chunks:
        return {"answer": "No documents uploaded yet. Please upload a document first.", "sources": []}
    context_texts = [c["text"] for c in chunks]
    answer = llm_module.generate(req.query, context_texts, req.temperature)
    return {"answer": answer, "sources": chunks, "temperature": req.temperature,
            "model": "groq" if llm_module._USE_GROQ else "mock"}


@app.post("/temperature-study")
def temperature_study(req: TempStudyRequest):
    chunks = retrieve(req.query)
    context_texts = [c["text"] for c in chunks] if chunks else [
        "This is a sample context for demonstration purposes. "
        "The system uses retrieval-augmented generation to ground responses in uploaded documents. "
        "Temperature controls the creativity and verbosity of generated responses."
    ]

    results = []
    for temp in TEMPERATURES:
        answer = llm_module.generate(req.query, context_texts, temp)
        words = answer.split()
        unique_ratio = round(len(set(words)) / max(len(words), 1), 3)
        results.append({
            "temperature": temp,
            "answer": answer,
            "metrics": {
                "word_count": len(words),
                "unique_word_ratio": unique_ratio,
                "sentence_count": answer.count(".") + answer.count("!") + answer.count("?"),
            },
        })
    return {"query": req.query, "results": results}
