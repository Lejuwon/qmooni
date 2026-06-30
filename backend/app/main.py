import os, sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.session import engine, Base
from app.core.config import settings
from app.api.routes import router as api_router
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# CORS 미들웨어 설정 (FastAPI 생성 직후)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 프론트엔드 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ① startup 이벤트로 테이블 생성
@app.on_event("startup")
def create_tables():
    print("▶️ [startup] Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)
    print("✅ [startup] Tables are ready.")

# ▶ 업로드된 파일들을 /uploaded_files/** 라우트로 서빙    
app.mount(
    "/uploaded_files",
    StaticFiles(directory="uploaded_files"),
    name="uploaded_files"
)

# API 라우터 등록
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"msg": "Welcome to Qmooni backend!"}