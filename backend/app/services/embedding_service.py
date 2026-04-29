import json
import math
import uuid
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.embeddings import DocumentEmbedding, USE_PGVECTOR
from app.agents.base import get_embeddings


async def upsert_embedding(db: AsyncSession, entity_type: str, entity_id: uuid.UUID, content: str):
    embeddings = get_embeddings()
    vec = await embeddings.aembed_query(content)

    await db.execute(
        delete(DocumentEmbedding).where(
            DocumentEmbedding.entity_type == entity_type,
            DocumentEmbedding.entity_id == entity_id,
        )
    )
    doc = DocumentEmbedding(
        entity_type=entity_type,
        entity_id=entity_id,
        content=content,
        embedding=vec if USE_PGVECTOR else json.dumps(vec),
        updated_at=datetime.utcnow(),
    )
    db.add(doc)
    await db.commit()


async def similarity_search(db: AsyncSession, query: str, k: int = 5) -> list[DocumentEmbedding]:
    embeddings = get_embeddings()
    vec = await embeddings.aembed_query(query)

    if USE_PGVECTOR:
        res = await db.execute(
            select(DocumentEmbedding)
            .order_by(DocumentEmbedding.embedding.cosine_distance(vec))
            .limit(k)
        )
        return list(res.scalars().all())

    # SQLite fallback — compute cosine in Python
    rows = (await db.execute(select(DocumentEmbedding))).scalars().all()
    scored: list[tuple[float, DocumentEmbedding]] = []
    for d in rows:
        if not d.embedding:
            continue
        try:
            doc_vec = json.loads(d.embedding)
        except (TypeError, ValueError):
            continue
        scored.append((_cosine(vec, doc_vec), d))
    scored.sort(key=lambda x: -x[0])
    return [d for _, d in scored[:k]]


def _cosine(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
