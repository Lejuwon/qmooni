import os
from typing import List
from langchain_community.vectorstores import FAISS
# from langchain_openai import OpenAIEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_core.documents import Document
from app.core.config import settings

# 11 21:21
def get_chunks_from_documents(
    user_topic_id: int,
    document_ids: List[int],
    db  # 현재 미사용
) -> List[Document]:
    """
    FAISS 벡터 저장소에서 특정 topic_id에 해당하는 chunk 중
    document_id와 type이 'summary'인 것만 추출
    """
    user_id = 1  # TODO: 인증으로 교체

    faiss_path = f"./faiss_store/user_{user_id}/topic_{user_topic_id}"
    if not os.path.exists(faiss_path):
        return []

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key
    )
    vs = FAISS.load_local(
        faiss_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    all_docs: List[Document] = list(vs.docstore._dict.values())

    # ✅ 요약 청크만 필터링
    filtered_chunks = [
        doc for doc in all_docs
        if int(doc.metadata.get("document_id", -1)) in document_ids
        and doc.metadata.get("type") == "summary"
    ]

    return filtered_chunks

