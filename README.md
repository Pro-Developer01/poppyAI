# poppyAI
#How to start the Project

cd infra/compose
docker compose up -d
# check: docker compose ps
# RabbitMQ UI  -> http://localhost:15672  (guest / guest)
# Qdrant UI    -> http://localhost:6333/dashboard


# To Run ingestion-consumer and query-api

# Terminal A — ingestion consumer
cd apps/worker && source .venv/bin/activate
python -m worker.consumer

# Terminal B — query API
cd apps/worker && source .venv/bin/activate
uvicorn worker.api:app --port 8000 --reload


#Final Step

Start the Nest JS server
cd apps/gateway 
npm run dev

# 1) Upload  (async ingestion shuru)
curl -F "file=@sample.pdf" http://localhost:3000/documents

# -> {"jobId":"a1b2...","documentId":"c3d4...","status":"processing"}



# 2) Status check (thodi der baad)
curl http://localhost:3000/jobs/a1b2...

# -> { ..., "status":"done" }   (ya "processing" / "failed")



# 3) Query
curl -X POST http://localhost:3000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the total invoice amount?"}'