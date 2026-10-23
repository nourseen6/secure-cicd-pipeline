# Secure CI/CD Pipeline 

[![CI](https://github.com/nourseen6/secure-cicd-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/nourseen6/secure-cicd-pipeline/actions/workflows/ci.yml)

A DevSecOps pipeline for a small Python web service. Every push is tested, scanned for leaked secrets, built into a container image, scanned for vulnerabilities, and published — and the pipeline **fails automatically** when it finds a critical issue.

The same pipeline runs on **GitHub Actions** and on **Jenkins**.

> 🚧 **Work in progress.** Built step by step as part of my [DevOps roadmap](https://github.com/nourseen6/roadmap). The checklist below shows what's done.

## Architecture

```mermaid
flowchart LR
    dev[Developer] -->|git push| gh[GitHub]
    gh --> ci{{CI pipeline<br/>GitHub Actions / Jenkins}}
    ci --> test[Unit tests]
    ci --> secrets[Secret scan<br/>gitleaks]
    test --> build[Docker build<br/>multi-stage]
    secrets --> build
    build --> scan[Image scan<br/>Trivy]
    scan -->|no CRITICAL| push[Push image]
    scan -->|CRITICAL found| fail[❌ Fail build]
    push --> reg[(GitHub Container<br/>Registry)]
    gh -.-> dep[Dependabot<br/>dependency PRs]
```

## Tech stack

| Area | Tools |
|---|---|
| Application | Python, FastAPI, PostgreSQL |
| Containers | Docker (multi-stage), Docker Compose |
| CI/CD | GitHub Actions, Jenkins |
| Security | gitleaks, Trivy, Dependabot |
| Scripting | Bash |

## Progress

- [x] Python API
- [x] PostgreSQL storage with parameterized queries
- [x] Unit tests
- [x] Multi-stage Dockerfile — image reduced from 1.67 GB to 222 MB, runs as a non-root user
- [x] Docker Compose for the app and database, with health checks and the password kept out of Git
- [x] GitHub Actions: test → build → push to the GitHub Container Registry
- [x] Secret scanning with gitleaks across the full Git history
- [x] Image scanning with Trivy — the image is pushed only if no fixable CRITICAL vulnerability is found
- [x] Dependabot for Python packages, the base image, and GitHub Actions
- [x] Every third-party action pinned to a commit SHA
- [ ] The same pipeline as a Jenkinsfile
- [x] Red run and green run documented — see [Security gates in action](#security-gates-in-action)

## Security gates in action

Each gate was tested on purpose, on a pull request that was then closed without merging.

| Scenario | 🔴 Blocked | 🟢 Fixed |
|---|---|---|
| **Hard-coded API key** in `app/config.py` | [gitleaks found it](https://github.com/nourseen6/secure-cicd-pipeline/actions/runs/40001783065) (`generic-api-key`); the image build was skipped | [Key moved to an environment variable](https://github.com/nourseen6/secure-cicd-pipeline/actions/runs/40001893687) and the leaking commit removed from history |
| **Outdated library**: `django==2.2.0` | [Trivy found 6 CRITICAL CVEs](https://github.com/nourseen6/secure-cicd-pipeline/actions/runs/40003321334), including CVE-2019-14234 (SQL injection); the image was not pushed | [Upgraded to Django 6.1.2](https://github.com/nourseen6/secure-cicd-pipeline/actions/runs/40003968577); the scan passes |

Pull requests: [#10](https://github.com/nourseen6/secure-cicd-pipeline/pull/10) and [#11](https://github.com/nourseen6/secure-cicd-pipeline/pull/11).

**Lesson from the secret demo:** deleting a leaked secret in a new commit is not enough — it stays in the Git history. The fix is to rotate the secret, load it from the environment, and remove it from history.

## Project structure

```
.
├── app/
│   ├── main.py             # FastAPI service
│   └── storage.py          # PostgreSQL or in-memory storage
├── tests/
│   └── test_main.py        # Unit tests
├── docs/                   # Diagrams and screenshots (coming soon)
├── Dockerfile              # Multi-stage, non-root image
├── docker-compose.yml      # App + PostgreSQL
├── .env.example            # Template for local secrets
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Test dependencies
├── README.md
└── LICENSE
```

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `POST` | `/shorten` | Takes `{"url": "https://..."}` and returns a short code |
| `GET` | `/{code}` | Redirects to the original URL, or `404` if the code is unknown |

Interactive docs are served at `/docs` when the app is running.

## Getting started

Requirements: Python 3.12+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Run the tests:

```bash
pytest
```

Run the app, then open http://127.0.0.1:8000/docs:

```bash
uvicorn app.main:app --reload
```

### With Docker

Pull the image the pipeline publishes:

```bash
docker run -d -p 8000:8000 ghcr.io/nourseen6/secure-cicd-pipeline:latest
```

Or build it yourself:

```bash
docker build -t secure-cicd-pipeline .
docker run -d -p 8000:8000 --name url-shortener secure-cicd-pipeline
```

The image is a multi-stage build on `python:3.14-slim`. It runs as a non-root user and has a built-in health check on `/health`.

Without a database, links are kept in memory and lost on restart.

### With Docker Compose (app + PostgreSQL)

```bash
cp .env.example .env    # then set your own POSTGRES_PASSWORD in .env
docker compose up -d --build
```

The app waits until PostgreSQL is healthy, and links are stored in a Docker volume, so they survive restarts. Stop everything with `docker compose down`.

## What I learned

A short write-up of the problems I hit and how I solved them will be added here.

## License

[MIT](LICENSE)
