# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import requests

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.core.config import settings
from app.core.security import create_access_token
from app.api.deps import get_current_user_id

router = APIRouter(tags=["auth"])

@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    # 1) 구글 토큰 교환
    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": str(settings.google_redirect_uri),
            "grant_type": "authorization_code",
        },
    )
    if not token_res.ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange token with Google"
        )
    access_token_google = token_res.json()["access_token"]

    # 2) 구글 프로필 조회
    profile = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token_google}"}
    ).json()

    # 3) DB에 사용자 저장 또는 조회
    user = db.query(User).filter_by(email=profile["email"]).first()
    if not user:
        user = User(
            email=profile["email"],
            name=profile.get("name"),
            image_url=profile.get("picture"),
            oauth_provider="google",
            oauth_subject=profile["id"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4) JWT 생성
    jwt_token = create_access_token({"sub": str(user.user_id)})

    # 5) RedirectResponse 로 프론트엔드로 보내면서 토큰을 쿼리 스트링에 실어 줍니다.
    base = str(settings.frontend_url).rstrip("/")
    redirect_url = f"{base}/auth/callback?token={jwt_token}"
    return RedirectResponse(redirect_url)

@router.get("/me", response_model=UserRead)
def read_users_me(current_user_id: str = Depends(get_current_user_id),
                  db: Session = Depends(get_db)):
    user = db.query(User).get(int(current_user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
