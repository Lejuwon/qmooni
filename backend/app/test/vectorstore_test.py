from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings

# embeddings 설정 (upload에서 쓴 것과 같게!)
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small", 
    openai_api_key=settings.openai_api_key
)
# 벡터 디비 경로
faiss_path = "./faiss_store"

# FAISS 로드
vs = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)

# 개수 확인
print("✅ 저장된 벡터 수:", vs.index.ntotal)

query = "기업가정신이란 무엇인가?"
results = vs.similarity_search(query, k=3)
for i, doc in enumerate(results):
    print(f"[{i+1}] {doc.page_content[:100]}...")
