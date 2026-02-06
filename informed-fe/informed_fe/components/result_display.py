import streamlit as st

from informed_fe.config.logging import get_logger
from informed_fe.models import AnalysisResult

logger = get_logger(__name__)

def display_results(result: AnalysisResult) -> None:
    logger.debug(f"Analysis result: {result}")

    st.write("**Ingredients and Health Assessments**")
    if result.assessments:
        data = [
            {
                "Ingredient": ingredient_name,
                "Rating": assessment.rating,
                "Reason": assessment.reason
            }
            for ingredient_name, assessment in result.assessments.items()
        ]
        st.table(data)
    else:
        st.write("No ingredients or assessments found.")
