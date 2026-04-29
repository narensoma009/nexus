"""Document embeddings table.

When DATABASE_URL is postgres, the embedding column uses pgvector for fast similarity.
When DATABASE_URL is sqlite (local mock dev), embedding is stored as JSON-encoded text
and similarity is computed in Python.
"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.config import settings
from app.models.base import Base


USE_PGVECTOR = settings.DATABASE_URL.lower().startswith("postgresql")


if USE_PGVECTOR:
    from pgvector.sqlalchemy import Vector

    class DocumentEmbedding(Base):
        __tablename__ = "document_embeddings"
        id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
        entity_type: Mapped[str] = mapped_column(String(100))
        entity_id: Mapped[uuid.UUID] = mapped_column(Uuid)
        content: Mapped[str] = mapped_column(Text)
        embedding = mapped_column(Vector(768), nullable=True)
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

else:

    class DocumentEmbedding(Base):
        __tablename__ = "document_embeddings"
        id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
        entity_type: Mapped[str] = mapped_column(String(100))
        entity_id: Mapped[uuid.UUID] = mapped_column(Uuid)
        content: Mapped[str] = mapped_column(Text)
        embedding: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
        updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
