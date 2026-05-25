"""
LLM abstraction: uses Groq when GROQ_API_KEY is set, falls back to MockLLM.

Supported Groq models (free tier):
  - llama-3.1-8b-instant   (fastest)
  - llama-3.3-70b-versatile (best quality)
  - mixtral-8x7b-32768      (long context)
"""
import os
from mock_llm import MockLLM

_mock = MockLLM()

try:
    from groq import Groq
    _groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
    _USE_GROQ = True
    print(f"✓ Groq LLM active (model: {os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')})")
except (ImportError, KeyError):
    _groq_client = None
    _USE_GROQ = False
    print("⚠  GROQ_API_KEY not set — using MockLLM (set the key to enable real responses)")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def generate(query: str, context_chunks: list[str], temperature: float) -> str:
    if not _USE_GROQ:
        return _mock.generate(query, context_chunks, temperature)

    context = "\n\n".join(
        f"[Chunk {i+1}]\n{chunk}" for i, chunk in enumerate(context_chunks)
    )
    # Groq caps temperature at 2.0; values above that raise an error
    safe_temp = min(float(temperature), 2.0)

    response = _groq_client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=safe_temp,
        max_tokens=512,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that answers questions strictly based on "
                    "the provided document context. Be concise and factual. "
                    "If the context does not contain enough information to answer the question, "
                    "say so clearly."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}",
            },
        ],
    )
    return response.choices[0].message.content
