from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id", ondelete="CASCADE"))
    chunk_index = Column(Integer)
    chunk_text = Column(Text, nullable=False)

    document = relationship("Document", back_populates="chunks")
