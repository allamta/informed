# Informed - Food Ingredient Health Analyzer

A full-stack containerized application that analyzes food ingredient labels using OCR and LLM, returning health assessments with caching to minimize API costs.

## How It Works

1. User uploads an image of a food product's ingredient list
2. OCR extracts text from the image (EasyOCR)
3. LLM identifies and cleans ingredient names (LangGraph + Groq)
4. LLM assesses each ingredient's health impact (healthy/unhealthy/neutral)
5. Results are cached in PostgreSQL to avoid redundant API calls

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ :9040
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                        │
│         Web UI for image upload and results display             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ :9030
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│                                                                 │
│   ┌──────────┐    ┌───────────┐    ┌──────────┐               │
│   │  EasyOCR │───▶│ LangGraph │───▶│ Groq API │               │
│   └──────────┘    └───────────┘    └──────────┘               │
│                          │                                      │
│                          ▼                                      │
│                   ┌────────────┐                               │
│                   │ PostgreSQL │ (LLM response cache)          │
│                   └────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend | FastAPI, Python 3.11, Pydantic, SQLAlchemy |
| Frontend | Streamlit |
| AI/ML | LangChain, LangGraph, Groq API, EasyOCR |
| Database | PostgreSQL |
| Containerization | Docker, Docker Compose |
| Monitoring | Prometheus, Grafana |

## Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend (Streamlit) | http://localhost:9040 | Web UI |
| Backend (FastAPI) | http://localhost:9030/docs | REST API with Swagger docs |
| Backend Metrics | http://localhost:9030/metrics | Prometheus metrics endpoint |
| Frontend Metrics | http://localhost:9041/metrics | Prometheus metrics endpoint |
| Grafana | http://localhost:3000 | Monitoring dashboards (no login required) |
| Prometheus | http://localhost:9090 | Metrics query interface |
| postgres-exporter | http://localhost:9187/metrics | PostgreSQL metrics |

## Quick Start

```bash
git clone <repository-url>
cd informed
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
docker compose up --build
```

## Monitoring

Full observability stack with Prometheus and Grafana using the RED method (Rate, Errors, Duration).

### Dashboard Panels

- **Backend (FastAPI)**: HTTP request rate, latency (p50/p95/p99), errors by status
- **Frontend (Streamlit)**: API call rate, latency, image uploads
- **Groq LLM API**: Request rate, errors by type, latency (p50/p95/p99)
- **OCR Service**: Processing rate, errors by type, duration
- **Cache Performance**: Hit rate gauge, hits vs misses over time
- **Database**: Read/write latency, PostgreSQL connections, transactions, and locks

### Metrics Types

- **Histograms**: Latency percentiles (LLM, OCR, DB read/write, HTTP requests)
- **Counters**: Request totals, errors (with labels for error type), cache hits/misses
- **Labels**: `operation` (read/write), `error_type` (timeout, invalid_json, ConnectionError), `status` (HTTP status codes), `handler` (API endpoint paths)

## Project Structure

```
informed/
├── docker-compose.yml
├── .env.example
├── how-to-run.md
├── informed-be/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── informed_be/
│       ├── main.py
│       ├── api/routes.py
│       ├── config/settings.py
│       ├── db/db.py
│       ├── metrics.py
│       ├── services/ocr_service.py
│       └── workflows/ingredient_graph.py
├── informed-fe/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── informed_fe/
│       ├── app.py
│       ├── config/settings.py
│       ├── components/result_display.py
│       └── metrics.py
├── prometheus/
│   └── prometheus.yml
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       └── dashboards/
├── scripts/
│   └── load_test.py
└── test-data/
    └── *.jpg
```

## Testing the Application

**Option 1: Browser UI**
- Open http://localhost:9040
- Upload an image of a food ingredient label
- View health assessments in real-time

**Option 2: Load Test Script (Direct API)**
```bash
python3 scripts/load_test.py
python3 scripts/load_test.py --loops 10
```
Bypasses the frontend and calls the backend API directly with test images from `test-data/` directory. Useful for generating metrics data and performance testing.
