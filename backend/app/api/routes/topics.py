# app/api/routes/topics.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.topic import TopicCreate, TopicRead, TopicUpdate
from app.models.topic import Topic as TopicModel
from app.api.deps import get_current_user_id  # user_id 추출용

router = APIRouter(tags=["topics"])

# @router.post("/", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
# def create_topic(
#     topic_in: TopicCreate,
#     db: Session = Depends(get_db),
#     current_user_id: int = Depends(get_current_user_id),
# ):
#     topic = TopicModel(
#         title=topic_in.title,
#         user_id=current_user_id,
#         # description=topic_in.description,
#     )
#     db.add(topic)
#     db.commit()
#     db.refresh(topic)
#     return topic

@router.post("/", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
def create_topic(
    topic_in: TopicCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    print(f"[DEBUG] 요청 받은 데이터: {topic_in}")
    print(f"[DEBUG] 현재 사용자 ID: {current_user_id}")

    topic = TopicModel(
        title=topic_in.title,
        user_id=current_user_id,
        # description=topic_in.description,
    )

    db.add(topic)
    db.commit()
    db.refresh(topic)

    print(f"[DEBUG] 생성된 토픽 ID: {topic.topic_id}")
    return topic

@router.post("/topics", response_model=TopicRead)
def create_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        new_topic = TopicModel(title=topic.title, user_id=user_id)
        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)
        return new_topic
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # 상세 에러 출력

@router.get("/", response_model=List[TopicRead])
def read_topics(
    current_user_id: str = Depends(get_current_user_id),  # ★ 로그인 사용자 가져오기
    db: Session = Depends(get_db),
):
    # current_user_id 는 sub 에서 뽑아낸 사용자 ID 문자열
    return (
        db.query(TopicModel)
          .filter(TopicModel.user_id == int(current_user_id))  # ★ 이 사용자 것만
          .order_by(TopicModel.created_at.desc())
          .all()
    )

@router.put("/{topic_id}", response_model=TopicRead)
def update_topic(
    topic_id: int,
    in_data: TopicUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    topic = (
        db.query(TopicModel)
          .filter(TopicModel.topic_id == topic_id,
                  TopicModel.user_id == current_user_id)
          .first()
    )
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # 변경 가능한 필드만 덮어쓰기
    if in_data.title is not None:
        topic.title = in_data.title
    # if in_data.description is not None:
    #     topic.description = in_data.description

    db.commit()
    db.refresh(topic)
    return topic

@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    topic = (
        db.query(TopicModel)
        .filter(TopicModel.topic_id == topic_id, 
                TopicModel.user_id == current_user_id)
        .first()
    )
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    db.delete(topic)
    db.commit()
    return
