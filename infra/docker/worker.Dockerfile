FROM python:3.12-slim

WORKDIR /app

# pehle sirf requirements copy — layer caching ka fayda (neeche samjhaya)
COPY apps/worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ab pura package
COPY apps/worker/worker ./worker

# default command: API. consumer ke liye K8s mein command override karenge.
CMD ["uvicorn", "worker.api:app", "--host", "0.0.0.0", "--port", "8000"]