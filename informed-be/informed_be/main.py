from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from informed_be.api.routes import router
from informed_be.config.settings import settings
from informed_be.config.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Ingredient Health Analyzer API",
    description="Backend API for analyzing food ingredients from images",
    version="0.1.0",
    debug=settings.DEBUG
)

app.include_router(router, prefix="/api")

Instrumentator().instrument(app).expose(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("informed_be.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
