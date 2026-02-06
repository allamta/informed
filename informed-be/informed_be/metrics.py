from prometheus_client import Counter, Histogram

GROQ_API_CALLS = Counter(
    "groq_api_calls_total",
    "Total number of calls made to Groq LLM API",
)

GROQ_API_ERRORS = Counter(
    "groq_api_errors_total",
    "Total number of failed Groq LLM API calls",
    labelnames=["error_type"],
)

GROQ_API_DURATION = Histogram(
    "groq_api_duration_seconds",
    "Time spent waiting for Groq LLM API responses",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

OCR_REQUESTS = Counter(
    "ocr_requests_total",
    "Total number of OCR text extraction requests",
)

OCR_ERRORS = Counter(
    "ocr_errors_total",
    "Total number of failed OCR text extractions",
    labelnames=["error_type"],
)

OCR_DURATION = Histogram(
    "ocr_duration_seconds",
    "Time spent on OCR text extraction",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
)

CACHE_HITS = Counter(
    "ingredient_cache_hits_total",
    "Number of ingredient lookups found in database cache",
)

CACHE_MISSES = Counter(
    "ingredient_cache_misses_total",
    "Number of ingredient lookups NOT found in database cache (requires LLM call)",
)

DB_QUERIES = Counter(
    "db_queries_total",
    "Total number of database queries",
    labelnames=["operation"],
)

DB_ERRORS = Counter(
    "db_errors_total",
    "Total number of failed database operations",
    labelnames=["operation"],
)

DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Time spent on database operations",
    labelnames=["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)
