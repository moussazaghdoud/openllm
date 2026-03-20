FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY app/ ./app/

ENV PORT=8000
EXPOSE 8000

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
