import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_documents_empty():
    response = client.get("/documents")
    assert response.status_code == 200
    assert "documents" in response.json()


def test_chat_no_documents():
    response = client.post("/chat", json={"query": "What is this about?", "temperature": 0.7})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data


def test_temperature_study_returns_four_results():
    response = client.post("/temperature-study", json={"query": "Explain the main concept"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 4
    temps = [r["temperature"] for r in data["results"]]
    assert set(temps) == {0.0, 0.5, 1.0, 1.5}


def test_temperature_study_metrics_present():
    response = client.post("/temperature-study", json={"query": "What is retrieval augmentation?"})
    data = response.json()
    for result in data["results"]:
        assert "metrics" in result
        assert "word_count" in result["metrics"]
        assert "unique_word_ratio" in result["metrics"]
        assert result["metrics"]["word_count"] > 0


def test_upload_invalid_extension():
    from io import BytesIO
    response = client.post(
        "/upload",
        files={"file": ("test.csv", BytesIO(b"a,b,c"), "text/csv")},
    )
    assert response.status_code == 400


def test_upload_txt_file():
    from io import BytesIO
    content = b"This is a test document about machine learning and neural networks. " * 20
    response = client.post(
        "/upload",
        files={"file": ("test_doc.txt", BytesIO(content), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "chunks" in data
    assert data["chunks"] > 0
