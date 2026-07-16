import uuid
from qdrant_client import models
from .chunking import load_and_chunk
from .embeddings import embed_texts
from .vectorstore import ensure_collection, upsert_chunks
from .db import update_job

def process_document(job: dict):
    job_id      = job["jobId"]
    document_id = job["documentId"]
    file_path   = job["filePath"]
    filename    = job.get("filename", "")

    try:
        ensure_collection()
        nodes  = load_and_chunk(file_path)
        texts  = [n.get_content() for n in nodes]
        vectors = embed_texts(texts)

        points = [
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vec,
                payload={
                    "document_id": document_id,
                    "filename":    filename,
                    "chunk_index": i,
                    "text":        node.get_content(),     # citation ke liye original text
                    "page":        node.metadata.get("page_label"),
                },
            )
            for i, (node, vec) in enumerate(zip(nodes, vectors))
        ]

        upsert_chunks(points)
        update_job(job_id, "done")
        print(f"[worker] done: {filename} ({len(points)} chunks)")

    except Exception as e:
        update_job(job_id, "failed", str(e))
        print(f"[worker] FAILED {filename}: {e}")
        raise
