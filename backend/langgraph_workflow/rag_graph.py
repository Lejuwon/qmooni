# ✅ 전체 구성: ask_question_with_rag() → LangGraph 노드 기반 재구성

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from app.core.config import settings
import os

# ✅ 상태 정의
class RAGState(TypedDict):
    messages: list
    user_id: int
    topic_id: int
    question: str
    file_name: Optional[str]
    file_choice_index: Optional[int]
    page: Optional[int]
    docs: Optional[list]
    answer: Optional[str]
    source_type: Optional[str]
    sources: Optional[list]

memory = MemorySaver()

# ✅ 1. 페이지 번호 추출 노드
def extract_page_number(state: RAGState) -> RAGState:
    import re
    match = re.search(r"(\d+)\s*페이지", state["question"])
    if match:
        state["page"] = int(match.group(1))
    return state

# ✅ 2. 문서 검색 노드 (RAG 검색)
def retrieve_docs(state: RAGState) -> RAGState:
    path = f"./faiss_store/user_{state['user_id']}/topic_{state['topic_id']}"
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key
    )
    vectorstore = FAISS.load_local(
        path, embeddings, allow_dangerous_deserialization=True
    )
    docs_with_scores = vectorstore.similarity_search_with_score(state["question"], k=10)
    all_docs = list(vectorstore.docstore._dict.values())

    # 페이지 기반 필터링
    if state["page"] is not None:
        filtered = [d for d in all_docs if str(d.metadata.get("page")) == str(state["page"])]
    else:
        filtered = [d for d, score in docs_with_scores if score >= 0.7]

    state["docs"] = filtered
    return state

# ✅ 3. 파일 이름 중복 처리 노드
def resolve_file_conflict(state: RAGState) -> RAGState:
    if not state["docs"]:
        return state

    filenames = list({doc.metadata.get("file_name") for doc in state["docs"]})

    if len(filenames) > 1 and state["file_name"] is None:
        if state["file_choice_index"] is not None:
            selected = filenames[state["file_choice_index"]]
            state["file_name"] = selected
        else:
            numbered = "\n".join([f"{i+1}. {f}" for i, f in enumerate(filenames)])
            state["answer"] = f"{state['page']}페이지는 여러 문서에 있습니다:\n{numbered}\n번호 또는 파일명을 입력해 주세요."
            state["source_type"] = "선택 요청"
            state["sources"] = [doc.metadata for doc in state["docs"]]
            state["docs"] = []  # 답변 유보
    return state

# ✅ 4. 답변 생성 노드
def generate_answer(state: RAGState) -> RAGState:
    if not state["docs"]:
        return state

    llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=settings.openai_api_key)
    context = "\n".join([
        f"[{doc.metadata.get('file_name')} / {doc.metadata.get('page')}p]\n{doc.page_content}"
        for doc in state["docs"]
        if state["file_name"] is None or doc.metadata.get("file_name") == state["file_name"]
    ])

    prompt = f"""
    다음은 질문과 참고 문서입니다. 문서를 기반으로 답변하세요.
    질문: {state['question']}
    문서:
    {context}
    답변:
    """
    result = llm.invoke(prompt).content.strip()
    state["answer"] = result
    state["source_type"] = "문서 기반"
    state["sources"] = [doc.metadata for doc in state["docs"]]
    return state

# ✅ LangGraph 정의
builder = StateGraph(RAGState)
builder.add_node("extract_page_number", extract_page_number)
builder.add_node("retrieve_docs", retrieve_docs)
builder.add_node("resolve_file_conflict", resolve_file_conflict)
builder.add_node("generate_answer", generate_answer)

builder.set_entry_point("extract_page_number")
builder.add_edge("extract_page_number", "retrieve_docs")
builder.add_edge("retrieve_docs", "resolve_file_conflict")
builder.add_edge("resolve_file_conflict", "generate_answer")
builder.add_edge("generate_answer", END)

graph = builder.compile(checkpointer=memory)

# ✅ 예시 실행
if __name__ == "__main__":
    result = graph.invoke({
        "messages": [HumanMessage(content="6페이지 요약해줘")],
        "user_id": 1,
        "topic_id": 3,
        "question": "6페이지 요약해줘",
        "file_name": None,
        "file_choice_index": 1,
    })
    print(result.get("answer"))
