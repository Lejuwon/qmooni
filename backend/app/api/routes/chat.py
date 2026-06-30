from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.topic import Topic
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionOut, ChatMessageOut
from app.api.deps import get_current_user_id
from app.services.chatbot import ask_question_with_rag

router = APIRouter(tags=["chat"])


# ✅ 1. 항상 새 세션을 생성하여 질문/답변 저장
@router.post("/{topic_id}", response_model=ChatResponse)
def start_new_chat_session(
    topic_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    topic = db.query(Topic).filter_by(topic_id=topic_id, user_id=user_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="해당 토픽을 찾을 수 없습니다.")

    # ✅ 1. 새 세션 생성
    session = ChatSession(
        user_id=user_id,
        topic_id=topic_id,
        title=request.message[:30]
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # ✅ 2. 사용자 메시지 저장
    user_msg = ChatMessage(
        session_id=session.session_id,
        sender_type="user",
        message=request.message
    )
    db.add(user_msg)

    # ✅ 3. RAG 기반 답변 생성
    try:
        rag_result = ask_question_with_rag(user_id=user_id, topic_id=topic_id, question=request.message)
        answer = rag_result["answer"]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # ✅ 4. 챗봇 메시지 저장
    bot_msg = ChatMessage(
        session_id=session.session_id,
        sender_type="bot",
        message=answer
    )
    db.add(bot_msg)
    db.commit()

    return ChatResponse(
    session_id=session.session_id,
    question=request.message,
    answer=rag_result["answer"],
    source_type=rag_result["source_type"],
    sources=rag_result["sources"]
)


# ✅ 2. 기존 세션에 이어서 대화하기
@router.post("/sessions/{session_id}", response_model=ChatResponse)
def ask_in_existing_session(
    session_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # ✅ 1. 세션 확인
    session = (
        db.query(ChatSession)
        .filter(ChatSession.session_id == session_id,
                ChatSession.user_id == user_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    topic_id = session.topic_id

    # ✅ 2. 사용자 메시지 저장
    user_msg = ChatMessage(
        session_id=session_id,
        sender_type="user",
        message=request.message
    )
    db.add(user_msg)

    # ✅ 3. RAG 기반 답변 생성
    try:
        rag_result = ask_question_with_rag(user_id=user_id, topic_id=topic_id, question=request.message)
        answer = rag_result["answer"]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # ✅ 4. 챗봇 메시지 저장
    bot_msg = ChatMessage(
        session_id=session_id,
        sender_type="bot",
        message=answer
    )
    db.add(bot_msg)
    db.commit()

    return ChatResponse(
        session_id=session_id,
        question=request.message,
        answer=answer
    )


# ✅ 3. 사용자의 세션 목록 조회
@router.get("/sessions", response_model=List[ChatSessionOut])
def list_chat_sessions(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.started_at.desc())
        .all()
    )
    return sessions


# ✅ 4. 특정 세션의 메시지 전체 조회
@router.get("/sessions/{session_id}", response_model=List[ChatMessageOut])
def get_chat_messages(
    session_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    session = db.query(ChatSession).filter_by(session_id=session_id, user_id=user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return messages

@router.get("/ping")
def ping():
    return {"message": "pong"}