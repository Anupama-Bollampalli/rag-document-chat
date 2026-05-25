import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mock_llm import MockLLM


def test_precise_response_is_short():
    llm = MockLLM()
    context = ["The system uses vector embeddings to retrieve relevant document chunks."]
    result = llm.generate("How does retrieval work?", context, temperature=0.0)
    assert len(result.split()) < 25, "Low temperature should produce concise responses"


def test_creative_response_is_longer():
    llm = MockLLM()
    context = ["The system uses vector embeddings to retrieve relevant document chunks."]
    precise = llm.generate("How does retrieval work?", context, temperature=0.0)
    creative = llm.generate("How does retrieval work?", context, temperature=1.5)
    assert len(creative.split()) > len(precise.split()), "High temperature should produce longer responses"


def test_temperature_produces_different_text():
    llm = MockLLM()
    context = ["Machine learning models learn patterns from training data."]
    query = "What is machine learning?"
    responses = {t: llm.generate(query, context, temperature=t) for t in [0.0, 0.5, 1.0, 1.5]}
    # All 4 temperatures should produce different responses
    unique = set(responses.values())
    assert len(unique) == 4, f"Expected 4 distinct responses, got {len(unique)}"


def test_empty_context_graceful():
    llm = MockLLM()
    result = llm.generate("What is AI?", [], temperature=0.5)
    assert isinstance(result, str) and len(result) > 0


def test_all_temperatures_return_strings():
    llm = MockLLM()
    context = ["Some context text about a topic."]
    for temp in [0.0, 0.3, 0.5, 0.7, 1.0, 1.2, 1.5]:
        result = llm.generate("test query", context, temperature=temp)
        assert isinstance(result, str) and len(result.strip()) > 0, f"Failed at temperature={temp}"
