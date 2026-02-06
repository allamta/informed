import streamlit as st
import requests

from informed_fe.components import display_results
from informed_fe.config import settings
from informed_fe.config.logging import setup_logging, get_logger
from informed_fe.metrics import (
    start_metrics_server,
    BACKEND_API_REQUESTS, BACKEND_API_ERRORS, BACKEND_API_DURATION,
    IMAGE_UPLOADS, IMAGE_SIZE_BYTES,
)
from informed_fe.models.schemas import AnalysisResult
from informed_fe.services import StorageService

setup_logging()
logger = get_logger(__name__)

start_metrics_server(port=9041)

st.set_page_config(page_title="Ingredient Health Analyzer", layout="wide")

st.title("Ingredient Health Analyzer")

uploaded_file = st.file_uploader("Upload an image of food ingredients", type=["jpg", "jpeg", "png"])

if uploaded_file:
    IMAGE_UPLOADS.inc()

    try:
        logger.info(f"Processing uploaded file: {uploaded_file.name}")
        image_bytes = StorageService.process_image(uploaded_file, compress=True)
        logger.debug(f"Image processed, size: {len(image_bytes)} bytes")

        IMAGE_SIZE_BYTES.observe(len(image_bytes))

        logger.info(f"Sending request to backend: {settings.INFORMED_BE_URL}/analyze")
        BACKEND_API_REQUESTS.inc()

        try:
            with BACKEND_API_DURATION.time():
                response = requests.post(
                    f"{settings.INFORMED_BE_URL}/analyze",
                    files={"file": (uploaded_file.name, image_bytes, uploaded_file.type)}
                )
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            error_type = type(e).__name__
            BACKEND_API_ERRORS.labels(error_type=error_type).inc()
            logger.error(f"API call failed: {str(e)}")
            st.error(f"API call failed: {str(e)}")
            raise

        logger.info(f"Backend response received: {response.status_code}")

        result = AnalysisResult(**response.json())

        display_results(result)

    except requests.exceptions.RequestException:
        pass
    except ValueError as e:
        logger.warning(f"Invalid response format: {str(e)}")
        st.error(f"Invalid response format: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        st.error(f"Error: {str(e)}")
