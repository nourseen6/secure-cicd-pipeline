from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_shorten_returns_a_code():
    response = client.post("/shorten", json={"url": "https://example.com"})

    assert response.status_code == 200
    body = response.json()
    assert body["code"]
    assert body["short_url"] == f"/{body['code']}"


def test_shorten_rejects_invalid_url():
    response = client.post("/shorten", json={"url": "not-a-url"})

    assert response.status_code == 422


def test_short_code_redirects_to_original_url():
    code = client.post("/shorten", json={"url": "https://example.com/page"}).json()["code"]

    response = client.get(f"/{code}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/page"


def test_unknown_code_returns_404():
    response = client.get("/does-not-exist")

    assert response.status_code == 404
