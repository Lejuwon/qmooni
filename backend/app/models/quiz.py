from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text, Boolean, TIMESTAMP, ARRAY
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime, timezone
from typing import List, Optional

class Quiz(Base):
    __tablename__ = "quizzes"

    quiz_id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.topic_id", ondelete="CASCADE"))
    document_id = Column(Integer, ForeignKey("documents.document_id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))

    questions = relationship("QuizQuestion", back_populates="quiz")
    document = relationship("Document")  


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    question_id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.quiz_id", ondelete="CASCADE"))
    question_type = Column(String)
    question_text = Column(Text, nullable=False)
    explanation = Column(Text)

    quiz = relationship("Quiz", back_populates="questions")
    mcq_detail = relationship("MCQQuestion", uselist=False, back_populates="question")
    ox_detail = relationship("OXQuestion", uselist=False, back_populates="question")


class MCQQuestion(Base):
    __tablename__ = "mcq_questions"

    question_id = Column(Integer, ForeignKey("quiz_questions.question_id", ondelete="CASCADE"), primary_key=True)
    choices = Column(ARRAY(Text), nullable=False)
    correct_answer = Column(Text, nullable=False)

    question = relationship("QuizQuestion", back_populates="mcq_detail")

class OXQuestion(Base):
    __tablename__ = "ox_questions"

    question_id = Column(Integer, ForeignKey("quiz_questions.question_id"), primary_key=True)
    correct_answer = Column(String(1))  # "O" 또는 "X" 저장 가능
    
    question = relationship("QuizQuestion", back_populates="ox_detail")

class QuestionChunk(Base):
    __tablename__ = "question_chunks"

    question_id = Column(Integer, ForeignKey("quiz_questions.question_id", ondelete="CASCADE"), primary_key=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.chunk_id", ondelete="CASCADE"), primary_key=True)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    attempt_id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.quiz_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    attempted_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    answers = relationship("QuizAnswer", back_populates="attempt", cascade="all, delete")


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    answer_id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.attempt_id", ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey("quiz_questions.question_id", ondelete="CASCADE"))
    user_answer = Column(Text)
    is_correct = Column(Boolean)
    
    attempt = relationship("QuizAttempt", back_populates="answers")