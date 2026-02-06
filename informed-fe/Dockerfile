FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY informed_fe ./informed_fe

RUN pip install --no-cache-dir .

CMD ["streamlit", "run", "informed_fe/app.py", "--server.port", "9040", "--server.address", "0.0.0.0"]
