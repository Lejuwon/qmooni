import os
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings

from app.core.config import settings

def get_topic_chatbot(user_id: int, topic_id: int) -> RetrievalQA:
    # 1. 벡터 저장소 경로 구성
    vectorstore_path = f"./faiss_store/user_{user_id}/topic_{topic_id}"
    
    # 2. 벡터 저장소 존재 여부 확인
    if not os.path.exists(os.path.join(vectorstore_path, "index.faiss")):
        raise ValueError("해당 토픽의 벡터 데이터가 존재하지 않습니다.")

    # 3. 임베딩 모델 및 벡터스토어 로드
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key
    )
    vectorstore = FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    # 4. LLM 및 QA 체인 구성
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        openai_api_key=settings.openai_api_key
    )
    retriever = vectorstore.as_retriever()

    # 5. QA 체인 반환
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )

    return qa

import os
from typing import Optional
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from app.utils.extractor import extract_page_number

    
# def ask_question_with_rag(user_id: int, topic_id: int, question: str, threshold: float = 0.7, file_name: Optional[str] = None):
#     vectorstore_path = f"./faiss_store/user_{user_id}/topic_{topic_id}"
#     if not os.path.exists(os.path.join(vectorstore_path, "index.faiss")):
#         raise ValueError("해당 토픽의 벡터 데이터가 존재하지 않습니다.")

#     embeddings = OpenAIEmbeddings(
#         model="text-embedding-3-small",
#         openai_api_key=settings.openai_api_key
#     )
#     vectorstore = FAISS.load_local(
#         vectorstore_path,
#         embeddings,
#         allow_dangerous_deserialization=True
#     )

#     llm = ChatOpenAI(
#         model="gpt-4",
#         temperature=0,
#         openai_api_key=settings.openai_api_key
#     )

#     # ✅ 1. 페이지 번호 추출
#     target_page = extract_page_number(question)

#     # ✅ 2. 전체 검색
#     all_docs_with_scores = vectorstore.similarity_search_with_score(question, k=10)

#     # ✅ 3. 페이지 필터링 + 문서 중복 확인
#     if target_page is not None:
#         candidate_docs = [
#             (doc, score)
#             for doc, score in all_docs_with_scores
#             if str(doc.metadata.get("page")) == str(target_page)
#         ]

#         file_names = list(set(doc.metadata.get("file_name") for doc, _ in candidate_docs))

#         if len(file_names) > 1 and not file_name:
#             file_choices = "\n".join([f"{i+1}. {name}" for i, name in enumerate(file_names)])
#             return {
#                 "answer": f"{target_page}페이지는 다음 여러 문서에서 발견됩니다:\n{file_choices}\n\n어떤 문서를 기준으로 할까요? 번호 또는 파일명을 입력해 주세요.",
#                 "source_type": "선택 요청",
#                 "sources": [doc.metadata for doc, _ in candidate_docs]
#             }

#         docs_with_scores = [
#             (doc, score)
#             for doc, score in candidate_docs
#             if file_name is None or doc.metadata.get("file_name") == file_name
#         ]
#     else:
#         docs_with_scores = all_docs_with_scores

#     print(f"[RAG DEBUG] 검색된 chunk 개수: {len(docs_with_scores)}")

#     # ✅ 4. threshold 필터
#     filtered_docs = [doc for doc, score in docs_with_scores if score >= threshold]

#     # ✅ fallback: 페이지 기준 실패 시 전체에서 재시도
#     if not filtered_docs and target_page is not None:
#         filtered_docs = [doc for doc, score in all_docs_with_scores if score >= threshold]

#     if filtered_docs:
#         context = "\n".join([
#             f"[{doc.metadata.get('file_name')} / {doc.metadata.get('page')}p]\n{doc.page_content}"
#             for doc in filtered_docs
#         ])

#         first_prompt = f"""
#         다음은 질문과 참고 문서입니다. 문서를 기반으로 최대한 자세히 답변하세요.

#         질문: {question}
#         문서:
#         {context}

#         답변:
#         """
#         first_answer = llm.invoke(first_prompt).content.strip()

#         relevance_prompt = f"""
#         질문: {question}
#         답변: {first_answer}

#         위 답변이 질문 의도와 본질적으로 일치하지 않거나, 문서 맥락에 너무 치우쳐 질문에 직접적인 답이 안 되면 '불일치'라고만 출력하세요.
#         잘 맞으면 '일치'라고만 출력하세요.
#         """
#         relevance = llm.invoke(relevance_prompt).content.strip()

#         if "불일치" in relevance:
#             fallback_prompt = f"""
#             다음 질문에 일반적인 GPT 지식을 바탕으로 답변하세요.

#             질문: {question}
#             답변:
#             """
#             answer = llm.invoke(fallback_prompt).content.strip()
#             return {
#                 "answer": answer,
#                 "source_type": "일반 지식 (문서 무시됨)",
#                 "sources": []
#             }

#         critique_prompt = f"""
#         질문: {question}
#         답변: {first_answer}

#         이 답변이 모호하거나 불완전한 경우 '불완전'이라고, 충분하면 '완전'이라고만 출력하세요.
#         """
#         judgment = llm.invoke(critique_prompt).content.strip()

#         if "불완전" in judgment:
#             revised_prompt = f"""
#             기존 답변: {first_answer}
#             문서:
#             {context}

#             위 내용을 참고하여 기존 답변을 더 명확하고 정확하게 보완하거나 수정하세요.
#             """
#             final_answer = llm.invoke(revised_prompt).content.strip()
#             return {
#                 "answer": final_answer,
#                 "source_type": "문서 기반 (보완됨)",
#                 "sources": [doc.metadata for doc in filtered_docs]
#             }
#         else:
#             return {
#                 "answer": first_answer,
#                 "source_type": "문서 기반",
#                 "sources": [doc.metadata for doc in filtered_docs]
#             }

#     # ✅ 6. 문서 자체가 없을 때 fallback
#     fallback_prompt = f"""
#     다음 질문에 일반적인 GPT 지식을 바탕으로 답변하세요.

#     질문: {question}
#     답변:
#     """
#     answer = llm.invoke(fallback_prompt).content.strip()
#     return {
#         "answer": answer,
#         "source_type": "일반 지식",
#         "sources": []
#     }
    
def ask_question_with_rag(user_id: int, topic_id: int, question: str, threshold: float = 0.7, file_name: Optional[str] = None):
    vectorstore_path = f"./faiss_store/user_{user_id}/topic_{topic_id}"
    if not os.path.exists(os.path.join(vectorstore_path, "index.faiss")):
        raise ValueError("해당 토픽의 벡터 데이터가 존재하지 않습니다.")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key
    )
    vectorstore = FAISS.load_local(
        vectorstore_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        openai_api_key=settings.openai_api_key
    )

    target_page = extract_page_number(question)
    all_docs_with_scores = vectorstore.similarity_search_with_score(question, k=10)

    if target_page is not None:
        candidate_docs = [
            (doc, score)
            for doc, score in all_docs_with_scores
            if str(doc.metadata.get("page")) == str(target_page)
        ]

        file_names = list(set(doc.metadata.get("file_name") for doc, _ in candidate_docs))
        if len(file_names) > 1 and not file_name:
            file_choices = "\n".join([f"{i+1}. {name}" for i, name in enumerate(file_names)])
            return {
                "answer": f"{target_page}페이지는 다음 여러 문서에서 발견됩니다:\n{file_choices}\n\n어떤 문서를 기준으로 할까요? 번호 또는 파일명을 입력해 주세요.",
                "source_type": "선택 요청",
                "sources": [doc.metadata for doc, _ in candidate_docs]
            }

        docs_with_scores = [
            (doc, score)
            for doc, score in candidate_docs
            if file_name is None or doc.metadata.get("file_name") == file_name
        ]
    else:
        docs_with_scores = all_docs_with_scores

    filtered_docs = [doc for doc, score in docs_with_scores if score >= threshold]

    if not filtered_docs and target_page is not None:
        filtered_docs = [doc for doc, score in all_docs_with_scores if score >= threshold]

    if filtered_docs:
        context = "\n".join([
            f"[{doc.metadata.get('file_name')} / {doc.metadata.get('page')}p]\n{doc.page_content}"
            for doc in filtered_docs
        ])

        first_prompt = f"""
        다음은 질문과 참고 문서입니다. 문서를 기반으로 최대한 자세히 답변하세요.

        질문: {question}
        문서:
        {context}

        답변:
        """
        first_answer = llm.invoke(first_prompt).content.strip()

        relevance_prompt = f"""
        질문: {question}
        답변: {first_answer}

        위 답변이 질문 의도와 본질적으로 일치하지 않거나, 문서 맥락에 너무 치우쳐 질문에 직접적인 답이 안 되면 '불일치'라고만 출력하세요.
        잘 맞으면 '일치'라고만 출력하세요.
        """
        relevance = llm.invoke(relevance_prompt).content.strip()

        if "불일치" in relevance:
            fallback_prompt = f"""
            다음 질문에 일반적인 GPT 지식을 바탕으로 답변하세요.

            질문: {question}
            답변:
            """
            answer = llm.invoke(fallback_prompt).content.strip()
            return {
                "answer": answer,
                "source_type": "일반 지식 (문서 무시됨)",
                "sources": []
            }

        critique_prompt = f"""
        질문: {question}
        답변: {first_answer}

        이 답변이 모호하거나 불완전한 경우 '불완전'이라고, 충분하면 '완전'이라고만 출력하세요.
        """
        judgment = llm.invoke(critique_prompt).content.strip()

        final_answer = first_answer
        if "불완전" in judgment:
            revised_prompt = f"""
            기존 답변: {first_answer}
            문서:
            {context}

            위 내용을 참고하여 기존 답변을 더 명확하고 정확하게 보완하거나 수정하세요.
            """
            final_answer = llm.invoke(revised_prompt).content.strip()

        # ✅ 문서 출처 정보 덧붙이기
        file_page_map = {}
        for doc in filtered_docs:
            file = doc.metadata.get("file_name", "알 수 없음")
            page = doc.metadata.get("page")
            if file not in file_page_map:
                file_page_map[file] = set()
            file_page_map[file].add(page)

        ref_summaries = []
        for file_name, pages in file_page_map.items():
            sorted_pages = sorted(pages)
            page_str = summarize_page_list(sorted_pages)
            ref_summaries.append(f"'{file_name}' 문서의 {page_str} 참고")
        refs = "자세한 내용은 " + ", ".join(ref_summaries) + "하시길 바랍니다."

        final_answer += f"\n\n{refs}"

        return {
            "answer": final_answer,
            "source_type": "문서 기반" if "불완전" not in judgment else "문서 기반 (보완됨)",
            "sources": [doc.metadata for doc in filtered_docs]
        }

    # fallback
    fallback_prompt = f"""
    다음 질문에 일반적인 GPT 지식을 바탕으로 답변하세요.

    질문: {question}
    답변:
    """
    answer = llm.invoke(fallback_prompt).content.strip()
    return {
        "answer": answer,
        "source_type": "일반 지식",
        "sources": []
    }
    
def summarize_page_list(pages: list[int]) -> str:
    if not pages:
        return ""
    ranges = []
    start = prev = pages[0]
    for page in pages[1:]:
        if page == prev + 1:
            prev = page
        else:
            ranges.append((start, prev))
            start = prev = page
    ranges.append((start, prev))
    return ", ".join(
        f"{s}페이지" if s == e else f"{s}~{e}페이지" for s, e in ranges
    )