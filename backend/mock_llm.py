"""
Temperature-aware mock LLM.
Replace MockLLM with an OpenAI/Anthropic/Groq client for production:
  from openai import OpenAI
  client = OpenAI(api_key="...")
  response = client.chat.completions.create(model="gpt-4o", temperature=temperature, messages=[...])
"""
import random
import re


class MockLLM:
    def generate(self, query: str, context_chunks: list[str], temperature: float) -> str:
        context = " ".join(context_chunks)
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', context) if len(s.strip()) > 20]
        if not sentences:
            sentences = ["The document contains relevant information about this topic."]

        if temperature <= 0.1:
            return self._precise(query, sentences)
        elif temperature <= 0.6:
            return self._balanced(query, sentences)
        elif temperature <= 1.1:
            return self._elaborated(query, sentences)
        else:
            return self._creative(query, sentences)

    def _precise(self, query: str, sentences: list[str]) -> str:
        core = sentences[0] if sentences else "No relevant content found."
        return f"Based on the document: {core}"

    def _balanced(self, query: str, sentences: list[str]) -> str:
        picked = sentences[:2] if len(sentences) >= 2 else sentences
        body = " ".join(picked)
        return f"The document addresses your query as follows: {body} This directly relates to {query.lower().rstrip('?')}."

    def _elaborated(self, query: str, sentences: list[str]) -> str:
        picked = sentences[:3] if len(sentences) >= 3 else sentences
        body = " ".join(picked)
        elaborations = [
            "It is worth noting that this topic has broader implications.",
            "Understanding this concept is foundational to the subject matter.",
            "This connects to several related ideas discussed in the document.",
        ]
        extra = random.choice(elaborations)
        return f"Great question! {body} {extra} Overall, the document provides a comprehensive view on {query.lower().rstrip('?')}."

    def _creative(self, query: str, sentences: list[str]) -> str:
        picked = sentences[:4] if len(sentences) >= 4 else sentences
        body = " ".join(picked)
        analogies = [
            "Think of it like a symphony where each instrument plays a unique role yet contributes to the whole.",
            "It's much like a garden — each element nurtures and depends on the others.",
            "Imagine a complex machine where every cog and gear serves a precise purpose in the grand design.",
        ]
        analogy = random.choice(analogies)
        return (
            f"What a fascinating inquiry! {body} "
            f"{analogy} "
            f"The interplay of ideas here opens doors to rich exploration — "
            f"from theoretical underpinnings to real-world applications of {query.lower().rstrip('?')}. "
            f"One could spend considerable time unpacking every nuance the document reveals on this subject!"
        )
