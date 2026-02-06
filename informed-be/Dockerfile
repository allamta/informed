FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY informed_be ./informed_be

RUN pip install --no-cache-dir .

RUN python -c "import easyocr; easyocr.Reader(['en'])"

CMD ["uvicorn", "informed_be.main:app", "--host", "0.0.0.0", "--port", "9030"]
