from fastapi.testclient import TestClient
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