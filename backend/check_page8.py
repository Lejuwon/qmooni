from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# 사용자 및 토픽 ID
user_id = 1
topic_id = 2

faiss_path = f"./faiss_store/user_{user_id}/topic_{topic_id}"

# 임베딩 모델 (저장 시 사용한 것과 동일해야 함)
embeddings = OpenAIEmbeddings()

# FAISS 벡터스토어 로드
vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)

# 전체 문서 chunk 가져오기
all_docs = list(vectorstore.docstore._dict.values())

# page == 6 필터링 (page=6으로 되어 있음. 원래 8을 원하면 숫자 수정)
page_8_chunks = [doc for doc in all_docs if doc.metadata.get("page") == 6]

# 출력
if page_8_chunks:
    print(f"✅ page=6인 chunk가 {len(page_8_chunks)}개 존재합니다.")
    for doc in page_8_chunks:
        print(f"- document_id: {doc.metadata.get('document_id')}, file_name: {doc.metadata.get('file_name')}, chunk_index: {doc.metadata.get('chunk_index')}, page: {doc.metadata.get('page')}")
else:
    print("❌ page=6인 chunk는 존재하지 않습니다.")