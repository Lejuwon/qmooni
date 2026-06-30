from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.core.config import settings
from langchain_core.documents import Document

def get_similar_chunks(text: str, chunks: list[str], top_k: int = 1) -> float:
    """
    하나의 문장(text)과 문서 chunk 리스트를 비교해
    가장 유사한 chunk와의 코사인 유사도를 반환한다.
    """
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key
    )

    # 임시 vector store를 만들어 유사도 검색
    docs = [Document(page_content=c) for c in chunks]
    faiss_index = FAISS.from_documents(docs, embeddings)

    results = faiss_index.similarity_search_with_score(text, k=top_k)
    if not results:
        return 0.0

    _, score = results[0]
    return 1 - score  # 유사도는 거리의 역수