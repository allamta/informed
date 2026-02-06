import json
from typing import Dict, List, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from informed_be.config.logging import get_logger
from informed_be.config.settings import settings
from informed_be.db import save_to_db, lookup_assessments_by_names
from informed_be.metrics import (
    CACHE_HITS, CACHE_MISSES,
    GROQ_API_CALLS, GROQ_API_ERRORS, GROQ_API_DURATION,
)
from informed_be.models.schemas import Ingredient, Assessment
from informed_be.services.ocr_service import OCRService

logger = get_logger(__name__)


class GraphState(TypedDict):
    image_bytes: bytes
    extracted_text: str
    ingredients: List[Ingredient]
    assessments: Dict[str, Assessment]

llm = ChatGroq(model=settings.MODEL)

def ocr_node(state: GraphState) -> GraphState:
    logger.debug("Starting OCR node")
    extracted = OCRService.extract_text(state["image_bytes"])

    ingredients = []
    for text, confidence in extracted:
        ingredients.append(Ingredient(name=text.strip(), confidence=confidence))

    state["ingredients"] = ingredients
    state["extracted_text"] = ",".join([ing.name for ing in ingredients])
    logger.info(f"OCR complete - extracted {len(ingredients)} ingredients")
    return state


def identify_node(state: GraphState) -> GraphState:
    logger.debug("Starting identify node")

    system_prompt = """You are a precise ingredient extraction tool. You ONLY output comma-separated ingredient lists with no additional text whatsoever."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Extract ingredients from: {text}\n\nOutput format: ingredient1, ingredient2, ingredient3")
    ])
    chain = prompt | llm

    response = chain.invoke({"text": state["extracted_text"]})
    cleaned_names = [name.strip() for name in response.content.split(",")]
    state["ingredients"] = [Ingredient(name=name.title()) for name in cleaned_names]

    logger.info(f"Identify complete - found {len(cleaned_names)} ingredients")
    return state


def assess_node(state: GraphState) -> GraphState:
    logger.debug("Starting assess node")
    logger.debug(f"Input ingredients: {', '.join([ing.name for ing in state['ingredients']])}")

    ingredient_names = [ing.name for ing in state["ingredients"]]
    cached_rows = lookup_assessments_by_names(ingredient_names)
    logger.info(f"Cache hit: {len(cached_rows)}/{len(ingredient_names)} ingredients found in DB")

    CACHE_HITS.inc(len(cached_rows))
    CACHE_MISSES.inc(len(ingredient_names) - len(cached_rows))

    assessments = {}
    for name, row in cached_rows.items():
        assessments[name] = Assessment(rating=row.rating, reason=row.reason)

    missing_ingredients = [name for name in ingredient_names if name not in cached_rows]
    if missing_ingredients:
        logger.info(f"Cache miss: calling Groq API for {len(missing_ingredients)} ingredients: {missing_ingredients}")
    else:
        logger.info("Full cache hit: no Groq API call needed")

    if missing_ingredients:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a certified nutrition expert. Assess food ingredients based on general nutritional science: 'healthy' for nutrient-dense/low-calorie items (e.g., vegetables), 'unhealthy' for high-sugar/processed items, 'neutral' for moderate ones. Provide brief, evidence-based reasons. Output raw JSON only."),
            ("human", "For these ingredients: {ingredients}, rate each as 'healthy', 'unhealthy', or 'neutral' with a brief reason. If unknown or empty, return empty dict. Format as: {{\"ingredient1\": {{\"rating\": \"healthy\", \"reason\": \"Rich in vitamins\"}}, \"ingredient2\": {{...}}}}"),
            ("human", "Example: Ingredients: sugar, kale\nOutput: {{\"sugar\": {{\"rating\": \"unhealthy\", \"reason\": \"High in empty calories, linked to obesity\"}}, \"kale\": {{\"rating\": \"healthy\", \"reason\": \"Packed with vitamins and fiber\"}}}}"),
            ("human", "Now assess: {ingredients}")])

        chain = prompt | llm
        ingredient_names_str = ", ".join(missing_ingredients)

        GROQ_API_CALLS.inc()
        try:
            with GROQ_API_DURATION.time():
                response = chain.invoke({"ingredients": ingredient_names_str})
        except Exception as e:
            error_type = type(e).__name__
            GROQ_API_ERRORS.labels(error_type=error_type).inc()
            logger.error(f"Groq API call failed: {error_type} - {str(e)}")
            raise

        logger.debug(f"LLM response for assessment: {response.content}")

        try:
            assessments_dict = json.loads(response.content)
            logger.debug(f"Parsed assessments: {assessments_dict}")
        except json.JSONDecodeError:
            GROQ_API_ERRORS.labels(error_type="invalid_json").inc()
            state["assessments"] = {}
            logger.error("JSON decode error in assessment response")
        else:
            for key, value in assessments_dict.items():
                try:
                    assessments[key] = Assessment(rating=value["rating"], reason=value["reason"])
                except (KeyError, ValueError) as e:
                    assessments[key] = Assessment(
                        rating="unknown",
                        reason=f"Parsing failed: {str(e)}"
                    )
                    logger.warning(f"Parsing failed for {key}: {str(e)}")

            save_to_db({k: v for k, v in assessments.items() if k not in cached_rows})

    state["assessments"] = assessments
    state["summary"] = "Overall assessment complete."
    logger.debug("Assess node complete")
    logger.debug(f"Final assessments: {state['assessments']}")
    return state


workflow = StateGraph(GraphState)
workflow.add_node("ocr", ocr_node)
workflow.add_node("identify", identify_node)
workflow.add_node("assess", assess_node)

workflow.add_edge("ocr", "identify")
workflow.add_edge("identify", "assess")
workflow.add_edge("assess", END)

workflow.set_entry_point("ocr")

graph = workflow.compile()


def analyze_ingredients(image_bytes: bytes) -> Dict:
    logger.info("Starting ingredient analysis")
    initial_state = {"image_bytes": image_bytes}
    final_state = graph.invoke(initial_state)

    return {
        "assessments": final_state.get("assessments", {})
    }
