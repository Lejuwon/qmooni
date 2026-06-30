from fastapi import APIRouter
from app.api.routes.auth import router as auth_router  # auth.py로부터 직접 import
from app.api.routes.topics import router as topics_router
from app.api.routes.documents import router as docs_router
from app.api.routes.chat import router as chat_router
from app.api.routes.quiz import router as quiz_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(topics_router, prefix="/topics", tags=["topics"])
router.include_router(chat_router,  prefix="/chat", tags=["chat"])
router.include_router(quiz_router, prefix="/quiz", tags=["quiz"])

# 토픽 범위 내 파일 업로드/조회
router.include_router(
    docs_router, 
    prefix="/topics/{topic_id}/documents", 
    tags=["documents"],
)

# 개별 문서 삭제
router.include_router(
    docs_router,
    prefix="/documents",
    tags=["documents"],
)
