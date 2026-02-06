# How to Run Informed

## Prerequisites

- Docker and Docker Compose installed
- A Groq API key (get one at https://console.groq.com)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd informed
   ```

2. **Create your environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and add your Groq API key**
   ```bash
   nano .env
   ```

4. **Start all services**
   ```bash
   docker compose up --build
   ```

## Environment Variables

All environment variables are required - no defaults.

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | `admin` |
| `POSTGRES_PASSWORD` | Database password | `admin` |
| `POSTGRES_DB` | Database name | `informed` |
| `GROQ_API_KEY` | Your Groq API key for LLM calls | `gsk_abc123...` |
| `MODEL` | LLM model to use | `openai/gpt-oss-120b` |
| `LOG_LEVEL` | Logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `PORT` | Backend API port | `9030` |
| `OCR_LANGUAGE` | OCR language code | `en` |
| `OCR_CONFIDENCE_THRESHOLD` | Min confidence for OCR text extraction | `0.5` |
| `MAX_UPLOAD_SIZE_MB` | Max image upload size in MB | `5` |
| `APP_ENV` | Environment | `dev` |

## Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| Frontend UI | http://localhost:9040 | Main application interface |
| Backend API Docs | http://localhost:9030/docs | Swagger API documentation |
| Grafana Dashboard | http://localhost:3000 | Monitoring dashboard (no login required) |
| Prometheus UI | http://localhost:9090 | Metrics query interface |

## Useful Commands

```bash
docker compose up --build -d          # Run in background
docker compose logs -f                # View all logs
docker compose logs -f backend        # View backend logs
docker compose down                   # Stop all services
docker compose down -v                # Stop and remove all data
docker compose ps                     # Check container status
docker exec -it informed-be bash      # Enter backend container
docker exec -it informed-db bash      # Enter database container
docker exec -it informed-db psql -U admin -d informed  # Connect to PostgreSQL directly
```

### PostgreSQL Commands
```sql
\dt                         -- List all tables
\d ingredients              -- Describe table structure
SELECT * FROM ingredients;  -- View cached ingredients
\q                          -- Exit
```

### Fresh start
```bash
docker compose down -v
docker compose up --build
```

## Troubleshooting

### Backend health check failing
The backend takes time to start because it loads EasyOCR models. Wait 1-2 minutes.

## Monitoring

The application includes a full observability stack using Prometheus and Grafana.

| Component | Purpose | Port |
|-----------|---------|------|
| Grafana | Pre-built dashboards for visualization | 3000 |
| Prometheus | Metrics collection and storage | 9090 |
| postgres-exporter | PostgreSQL database metrics (PostgreSQL doesn't expose Prometheus metrics natively) | 9187 |

### Dashboard Panels

- **Backend (FastAPI)**: HTTP request rate, latency (p50/p95/p99), errors by status
- **Frontend (Streamlit)**: API call rate, latency, image uploads
- **Groq LLM API**: Request rate, errors by type, latency (p50/p95/p99)
- **OCR Service**: Processing rate, errors by type, duration
- **Cache Performance**: Hit rate gauge, hits vs misses over time
- **Database**: Read/write latency, PostgreSQL connections, transactions, and locks

### Metrics Endpoints

| Service | Metrics URL |
|---------|-------------|
| Backend | http://localhost:9030/metrics |
| Frontend | http://localhost:9041/metrics |
| PostgreSQL | http://localhost:9187/metrics |

## Load Testing

A load test script is provided to test the backend API directly.

```bash
python3 scripts/load_test.py
python3 scripts/load_test.py --loops 10
python3 scripts/load_test.py --help
```

