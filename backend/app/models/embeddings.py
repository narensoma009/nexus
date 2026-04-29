import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.models.base import Base


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    content: Mapped[str] = mapped_column(Text)
    embedding = mapped_column(Vector(768))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
