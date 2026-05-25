# RAG Document Chat

A Retrieval-Augmented Generation (RAG) system that lets you upload documents and chat with them. Includes a **Temperature Study** feature that visually demonstrates how LLM temperature affects response style.

## Architecture

```
┌─────────────────┐     ┌──────────────────────────────────────┐
│   React Frontend │────▶│           FastAPI Backend             │
│  (Vite + TS)     │     │                                      │
│  • Chat UI       │     │  ┌─────────────┐  ┌──────────────┐  │
│  • Doc Upload    │◀────│  │ RAG Engine  │  │  Mock LLM    │  │
│  • Temp Study    │     │  │             │  │ (swap for    │  │
└─────────────────┘     │  │ SentenceT.  │  │  OpenAI etc) │  │
                        │  │ ChromaDB    │  └──────────────┘  │
                        │  └─────────────┘                    │
                        └──────────────────────────────────────┘
```

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.9-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green) ![React](https://img.shields.io/badge/React-18-61dafb) ![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue) ![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4-orange)

## Setup

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# API runs at http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# UI runs at http://localhost:5173
```

## Features

- **Document Ingestion**: Upload PDF or TXT files → chunked into 500-char segments with 50-char overlap → embedded with `all-MiniLM-L6-v2` → stored in ChromaDB
- **Semantic Search**: Query embedding compared against stored chunks using cosine similarity
- **Temperature Study**: Same query answered at temperatures 0.0, 0.5, 1.0, 1.5 with metrics comparison chart

## Swapping in a Real LLM

In `backend/mock_llm.py`, replace `MockLLM.generate` with:

```python
from openai import OpenAI
client = OpenAI(api_key="YOUR_KEY")

def generate(self, query, context_chunks, temperature):
    context = "\n".join(context_chunks)
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
            {"role": "system", "content": f"Answer using this context:\n{context}"},
            {"role": "user", "content": query},
        ]
    )
    return response.choices[0].message.content
```

## Deployment

**Backend** → Hugging Face Spaces (use the provided `Dockerfile`)  
**Frontend** → GitHub Pages (`npm run build` → push `dist/` to `gh-pages` branch)

## Screenshots

| Chat Interface | Temperature Study |
|---|---|
| *(screenshot)* | *(screenshot)* |
