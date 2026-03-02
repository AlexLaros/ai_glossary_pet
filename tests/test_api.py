from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_n_terms():
    response = client.post(
        "/glossary",
        data={"n_terms": 100},
        files={"file": ("test.pdf", b"%PDF-1.4 fake content", "application/pdf")}
    )
    assert response.status_code == 400
    assert "n_terms" in response.json()["detail"]


@patch("app.main.extract_text_from_pdf")
@patch("app.main.build_glossary_llm")
def test_glossary_success_with_mocked_pipeline(mock_llm, mock_extract):
    mock_extract.return_value = "Some extracted scientific text."
    mock_llm.return_value = [
        {"term": "Term A", "definition": "Def A", "example": "Example A"},
        {"term": "Term B", "definition": "Def B", "example": "Example B"},
    ]

    resp = client.post(
        "/glossary",
        data={"n_terms": 10},
        files={"file": ("paper.pdf", b"fake-bytes", "application/pdf")},
    )

    assert resp.status_code == 200
    body = resp.json()

    assert body["source"]["filename"] == "paper.pdf"
    assert body["n_terms_requested"] == 10
    assert body["terms_returned"] == 2
    assert isinstance(body["items"], list)
    assert body["items"][0]["term"] == "Term A"

    mock_extract.assert_called_once()
    mock_llm.assert_called_once()
