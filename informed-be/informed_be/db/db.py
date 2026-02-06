from typing import Dict, List

from sqlalchemy import Column, Integer, String, DateTime, func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from informed_be.config.settings import settings
from informed_be.config.logging import get_logger
from informed_be.models.schemas import Assessment
from informed_be.metrics import DB_QUERIES, DB_ERRORS, DB_QUERY_DURATION

logger = get_logger(__name__)

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class IngredientDB(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    rating = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

Base.metadata.create_all(bind=engine)

def save_to_db(assessments: Dict[str, Assessment]):
    DB_QUERIES.labels(operation="write").inc()
    session = SessionLocal()
    try:
        with DB_QUERY_DURATION.labels(operation="write").time():
            for name, assessment in assessments.items():
                normalized_name = name.lower().strip()
                existing = session.query(IngredientDB).filter_by(name=normalized_name).first()
                if existing:
                    logger.debug(f"Skipping {name}: already exists in database")
                    continue
                db_item = IngredientDB(
                    name=normalized_name,
                    rating=assessment.rating,
                    reason=assessment.reason
                )
                session.add(db_item)
                logger.debug(f"Added {normalized_name} to session")
            session.commit()
        logger.info("Successfully saved new assessments to database")
    except Exception as e:
        DB_ERRORS.labels(operation="write").inc()
        session.rollback()
        logger.error(f"DB save failed: {str(e)}")
    finally:
        session.close()

def lookup_assessments_by_names(names: List[str]) -> Dict[str, IngredientDB]:
    logger.debug("Starting lookup_assessments_by_names")
    DB_QUERIES.labels(operation="read").inc()
    session = SessionLocal()
    assessments = {}
    try:
        with DB_QUERY_DURATION.labels(operation="read").time():
            for name in names:
                normalized_name = name.lower().strip()
                logger.debug(f"Looking up ingredient: {name} (normalized: {normalized_name})")
                existing = session.query(IngredientDB).filter_by(name=normalized_name).first()
                if existing:
                    assessments[name] = existing
                    logger.debug(f"Found IngredientDB for {name}: rating={existing.rating}, reason={existing.reason}")
                else:
                    logger.debug(f"No assessment found for {name}")
        logger.debug("Completed lookup_assessments_by_names")
        return assessments
    except Exception as e:
        DB_ERRORS.labels(operation="read").inc()
        logger.error(f"DB lookup failed: {str(e)}")
        return assessments
    finally:
        session.close()
