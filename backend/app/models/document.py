from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.document_chunk import DocumentChunk

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.topic_id", ondelete="CASCADE"))
    file_name = Column(Text, nullable=False)
    file_type = Column(Text)
    file_url = Column(Text, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    topic = relationship("Topic", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete")