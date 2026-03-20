FROM python:3.11-slim

WORKDIR /app

# System deps for building native extensions
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model for Presidio
RUN python -m spacy download en_core_web_sm

# Verify it works
RUN python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy OK:', nlp.meta['name'])"
RUN python -c "from presidio_analyzer import AnalyzerEngine; print('Presidio OK')"

# Copy application code
COPY app/ ./app/

# Railway sets PORT env var
ENV PORT=8000
EXPOSE 8000

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
