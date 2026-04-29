import uuid
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.embeddings import DocumentEmbedding
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
        embedding=vec,
        updated_at=datetime.utcnow(),
    )
    db.add(doc)
    await db.commit()


async def similarity_search(db: AsyncSession, query: str, k: int = 5) -> list[DocumentEmbedding]:
    embeddings = get_embeddings()
    vec = await embeddings.aembed_query(query)
    res = await db.execute(
        select(DocumentEmbedding)
        .order_by(DocumentEmbedding.embedding.cosine_distance(vec))
        .limit(k)
    )
    return list(res.scalars().all())
