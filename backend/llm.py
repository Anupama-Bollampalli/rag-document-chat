"""
LLM abstraction: uses Groq when GROQ_API_KEY is set, falls back to MockLLM.
"""
import os
from mock_llm import MockLLM

_mock = MockLLM()
_USE_GROQ = False
_groq_client = None

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

try:
    from groq import Groq
    _api_key = os.environ.get("GROQ_API_KEY", "")
    if _api_key:
        _groq_client = Groq(api_key=_api_key)
        _USE_GROQ = True
        print(f"✓ Groq LLM active (model: {GROQ_MODEL})")
    else:
        print("⚠  GROQ_API_KEY not set — using MockLLM")
except Exception as e:
    print(f"⚠  Groq init failed ({e}) — using MockLLM")


def generate(query: str, context_chunks: list[str], temperature: float) -> str:
    if not _USE_GROQ or _groq_client is None:
        return _mock.generate(query, context_chunks, temperature)

    context = "\n\n".join(
        f"[Chunk {i+1}]\n{chunk}" for i, chunk in enumerate(context_chunks)
    )
    try:
        response = _groq_client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=min(float(temperature), 2.0),
            max_tokens=512,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that answers questions strictly based on "
                        "the provided document context. Be concise and factual. "
                        "If the context does not contain enough information, say so clearly."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}",
                },
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq call failed: {e} — falling back to mock")
        return _mock.generate(query, context_chunks, temperature)
