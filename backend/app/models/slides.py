import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PPTTemplate(Base):
    __tablename__ = "ppt_templates"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    tags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    slide_count: Mapped[int] = mapped_column(Integer)
    blob_path: Mapped[str] = mapped_column(String(500))
    placeholder_map: Mapped[str] = mapped_column(Text)
    uploaded_by: Mapped[str] = mapped_column(String(255))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
