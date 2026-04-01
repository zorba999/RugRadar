FROM python:3.12-slim

RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.dev.txt

RUN cd frontend && npm install && npm run build

EXPOSE 8000
CMD ["sh", "-c", "python -m uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]
