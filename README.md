# poppyAI

# PoppyAI — Agentic Document Intelligence Platform

Upload your documents. Ask questions. Get answers with citations back to the exact source.

PoppyAI is a production-shaped RAG system, not a notebook demo. A LangGraph agent
decides how to answer each question — search your documents, search the web, or
break a complex question into sub-questions — then grades what it retrieved and
rewrites its own query if the results are weak.

It's built as a polyglot system on purpose: a NestJS gateway handles uploads and
API traffic, a Python/FastAPI worker does the AI work, and RabbitMQ sits between
them so a 200-page PDF doesn't block a web request.

**What makes it different from a "chat with your PDF" demo:**
- Every agent step is traced with Langfuse
- Answer quality is scored with Ragas (faithfulness, relevancy, context precision)
  against a golden dataset — so changes can be measured, not guessed
- Two-level caching (exact + semantic) to keep token costs down
- Custom MCP server exposing tools to the agent
- Kubernetes manifests with proper stateful/stateless separation





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
