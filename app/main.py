import secrets

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from app.storage import create_store

app = FastAPI(title="Secure CI/CD Demo")

store = create_store()


class ShortenRequest(BaseModel):
    url: HttpUrl


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shorten")
def shorten(request: ShortenRequest):
    code = secrets.token_urlsafe(4)
    store.save(code, str(request.url))
    return {"code": code, "short_url": f"/{code}"}


@app.get("/{code}")
def redirect(code: str):
    url = store.get(code)
    if url is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    return RedirectResponse(url)
