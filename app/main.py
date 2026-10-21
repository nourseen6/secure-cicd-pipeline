import secrets

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="Secure CI/CD Demo")

links: dict[str, str] = {}


class ShortenRequest(BaseModel):
    url: HttpUrl


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/shorten")
def shorten(request: ShortenRequest):
    code = secrets.token_urlsafe(4)
    links[code] = str(request.url)
    return {"code": code, "short_url": f"/{code}"}


@app.get("/{code}")
def redirect(code: str):
    if code not in links:
        raise HTTPException(status_code=404, detail="Short link not found")
    return RedirectResponse(links[code])
