from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import shutil, os
from typing import List

from app.db.session        import get_db
from app.api.deps          import get_current_user_id
from app.models.document   import Document as DocumentModel
from app.models.topic      import Topic      as TopicModel
from app.schemas.document  import DocumentRead
from app.services.vector_store import process_and_embed
from app.services.vector_store import remove_doc_vs

router = APIRouter(tags=["documents"])

# 업로드한 파일을 서버 디스크에 저장하고, DB에 메타데이터를 남깁니다.
@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED
)
def upload_document(
    topic_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    # 1) topic이 이 user 소유인지 확인
    topic = (
        db.query(TopicModel)
          .filter(TopicModel.topic_id == topic_id,
                  TopicModel.user_id == user_id)
          .first()
    )
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # 2) 디스크 저장 경로 결정 (예: ./uploaded_files/{user_id}/{topic_id}/)
    upload_dir = f"uploaded_files/{user_id}/{topic_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3) DB에 기록
    doc = DocumentModel(
        topic_id=topic_id,
        file_name=file.filename,
        file_type=file.content_type,
        file_url = file_path,  # 혹은 외부 스토리지 URL
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # 4) 텍스트 추출 및 벡터 저장 
    # 0605추가 - umD
    process_and_embed(file_path, file.filename, user_id, topic_id, doc.document_id)
    
    return doc

# 이 토픽에 속한 문서들 리스트를 반환
@router.get("", response_model=List[DocumentRead])
def list_documents(
    topic_id: int,
    db:   Session = Depends(get_db),
    user_id: int  = Depends(get_current_user_id),
):
    # 소유자 확인(생략해도 무방)
    db.query(TopicModel).filter(
        TopicModel.topic_id == topic_id,
        TopicModel.user_id    == user_id
    ).first() or HTTPException(404)

    return (
        db.query(DocumentModel)
          .filter(DocumentModel.topic_id == topic_id)
          .order_by(DocumentModel.uploaded_at.desc())
          .all()
    )

@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="문서 삭제"
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    # 1) 해당 문서가 존재하는지, 그리고 이 유저 소유의 토픽에 속해 있는지 확인
    doc = (
        db.query(DocumentModel)
            .join(TopicModel, DocumentModel.topic_id == TopicModel.topic_id)
            .filter(
                DocumentModel.document_id == document_id,
                TopicModel.user_id == user_id
            )
        #   .join(DocumentModel.topic)        # DocumentModel.topic 관계가 있다고 가정
        #   .filter(DocumentModel.document_id == document_id)
        #   .filter(doc := DocumentModel,  ) # 그냥 가독성 위해 남김
        #   .filter(DocumentModel.topic.has(owner_id=user_id))
            .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 추가 - 0604
    topic_id = doc.topic_id
    
    # 2-1) 벡터 저장소에서 해당 문서의 벡터 제거 - 추가(0604)
    # try:
    #     remove_doc_vs(user_id, topic_id, document_id)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"벡터 제거 실패: {str(e)}")
    
    # 2-2) DB에서 삭제
    db.delete(doc)
    db.commit()
    # 204 No Content 응답
    return