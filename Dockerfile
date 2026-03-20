FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY app/ ./app/

EXPOSE 8000

# Railway injects PORT automatically — do not hardcode it
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
