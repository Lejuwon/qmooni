from langchain.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
import os

@tool
def retrieve_context_from_vectorstore(user_id: int, topic_id: int, query: str):
    """FAISS 벡터 DB에서 관련 컨텍스트 검색"""
    vectorstore_path = f"./faiss_store/user_{user_id}/topic_{topic_id}"
    if not os.path.exists(os.path.join(vectorstore_path, "index.faiss")):
        return "[오류] 벡터 데이터가 존재하지 않습니다."

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=settings.openai_api_key)
    vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
    docs_with_scores = vectorstore.similarity_search_with_score(query, k=5)

    results = [f"[{doc.metadata.get('file_name')} / {doc.metadata.get('page')}p]\n{doc.page_content}" for doc, score in docs_with_scores if score >= 0.7]
    return "\n\n".join(results) if results else "관련 문서 내용을 찾을 수 없습니다."