from qdrant_client import QdrantClient, models
from .config import settings

client = QdrantClient(url=settings.qdrant_url)
COLLECTION = "documents"

def ensure_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=models.VectorParams(
                size=settings.embed_dim,
                distance=models.Distance.COSINE,   # standard for text embeddings
            ),
        )

def upsert_chunks(points: list[models.PointStruct]):
    client.upsert(collection_name=COLLECTION, points=points)

def search(query_vector, top_k: int, document_id: str | None = None):
    query_filter = None
    if document_id:
        # if you need to search only inside a specific document
        query_filter = models.Filter(must=[
            models.FieldCondition(key="document_id",
                                  match=models.MatchValue(value=document_id))
        ])
    res = client.query_points(            # NOTE: new API. old .search() is legacy
        collection_name=COLLECTION,
        query=query_vector,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True,
    )
    return res.points   # list[ScoredPoint] -> .id, .score, .payload