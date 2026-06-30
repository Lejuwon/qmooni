import os
from openai import OpenAI
import re
from typing import Tuple, List
from collections import defaultdict
import random
from langchain.schema import Document
from dotenv import load_dotenv
load_dotenv()
# 환경변수에서 API 키 로드
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_mcq_from_paragraph(paragraph: str) -> str:
    """
    주어진 문단을 기반으로 객관식 문제와 해설을 생성합니다.
    형식은 다음과 같습니다:
    질문: ...
    A. ...
    B. ...
    C. ...
    D. ...
    정답: B
    해설: ...
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 한국어 객관식 문제를 만드는 AI야.\n"
                        "\n"
                        "질문을 만들 때 다음 지침을 반드시 지켜:\n"
                        "- '위 문단', '위 내용', '이 글', '다음 글' 같은 상대적 표현은 **절대 사용하지 마**.\n"
                        "- 질문은 **문맥과 상관없이 독립적으로 이해 가능하게 명확하게 작성**해.\n"
                        "- 문단 내용 중 핵심 개념, 정의, 이유, 목적, 과정, 특징, 사실/의견 구분 등을 물어봐.\n"
                        "- 단순 암기보다는 **이해력을 평가할 수 있는 질문**을 만들어.\n"
                        "\n"
                        "다음은 좋은 질문의 예시야:\n"
                        "- 'OO에 대한 설명으로 옳은 것은?'\n"
                        "- 'OO의 목적은 무엇인가?'\n"
                        "- 'OO가 필요한 이유로 알맞은 것은?'\n"
                        "- '다음 중 OO에 해당하지 않는 것은?'\n"
                        "- 'OO에 대한 내용으로 알맞지 않은 것은?'\n"
                        "- 'OO의 특징으로 적절하지 않은 것은?'\n"
                        "- 'OO의 절차로 옳은 순서는?'\n"
                        "- 'OO에 대한 설명으로 옳지 않은 것은?'\n"
                        "\n"
                        "❗주의사항:\n"
                        "- 해설에서는 보기의 알파벳 (A, B, C, D)을 절대 언급하지 마. 대신 각 보기에 담긴 내용을 직접 언급하면서 설명해.\n"
                        "  예) '전문가 의견은 참고자료일 수 있지만 계량적 예측보다 신뢰도가 낮다.' 처럼 설명해.\n"
                        "\n"
                        "출력 형식은 다음과 같아:\n"
                        "질문: ...\n"
                        "A. ...\n"
                        "B. ...\n"
                        "C. ...\n"
                        "D. ...\n"
                        "정답: B\n"
                        "해설: 정답이 맞는 이유와 오답이 틀린 이유를 설명해줘."
                    )
                },
                {
                    "role": "user",
                    "content": f"다음 문단을 기반으로 객관식 문제를 만들어줘:\n\n{paragraph}"
                }
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()
        return content

    except Exception as e:
        return f"문제 생성 실패: {str(e)}"
    
def parse_mcq_response(response: str) -> Tuple[str, List[str], str, str]:
    """
    OpenAI 응답 텍스트에서 질문, 보기 리스트, 정답, 해설을 추출한다.
    """
    lines = response.strip().splitlines()
    question = ""
    choices = []
    correct_answer = ""
    explanation = ""

    cleaned_lines = [re.sub(r"[|+]", "", line).strip() for line in lines if line.strip()]

    for line in cleaned_lines:
        if line.startswith("질문:"):
            question = line.replace("질문:", "").strip()
        elif re.match(r"^[A-D]\.", line):
            choices.append(line.split(".", 1)[1].strip())
        elif line.startswith("정답:"):
            correct_letter_match = re.search(r"정답:\s*([A-D])", line)
            if correct_letter_match:
                correct_letter = correct_letter_match.group(1)
                try:
                    index = "ABCD".index(correct_letter)
                    correct_answer = choices[index]
                except (ValueError, IndexError):
                    raise ValueError(f"정답 '{correct_letter}'가 보기와 매칭되지 않음")
            else:
                raise ValueError("정답 형식이 올바르지 않음")
        elif line.startswith("해설:") or line.startswith("설명:"):
            explanation = line.split(":", 1)[1].strip()

    if not question or not choices or not correct_answer:
        raise ValueError("질문 또는 보기 또는 정답이 비어 있음")

    return question, choices, correct_answer, explanation

def summarize_document(chunks: List[str]) -> str:
    all_text = "\n\n".join(chunks)
    prompt = "다음은 문서 전체 내용입니다. 이 내용을 기반으로 중요한 핵심 내용만 요약해줘:\n\n" + all_text

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    summary = response.choices[0].message.content.strip()
    
    print("요약 결과:\n", summary)  # 요약된 결과 출력
    
    return summary

def split_summary_to_chunks(summary: str, chunk_size=100) -> list[str]:
    return [summary[i:i + chunk_size] for i in range(0, len(summary), chunk_size)]

# def generate_questions_from_summary_chunks(chunks: List[Document], number_of_questions: int) -> List[Tuple[str, List[str], str, str]]:
#     # 1. 페이지별 텍스트 묶기
#     pages = defaultdict(list)
#     for chunk in chunks:
#         page = chunk.metadata.get("page", 0)
#         pages[page].append(chunk.page_content)

#     # 2. 페이지별 요약 + 요약 분할
#     summary_chunks = []
#     for page_num, texts in pages.items():
#         summary = summarize_document(chunks)  # <- chunks는 List[Document]
#         summary_chunks = split_summary_to_chunks(summary)  # <- List[str]
#         selected_chunks = summary_chunks[:request.numberOfQuestions]
#         print(f"페이지 {page_num} 요약:\n{summary}\n")
#         print(f"페이지 {page_num} 요약 청크 리스트:")
#         for chunk in selected_chunks:  # <- chunk는 str
#             raw_response = generate_mcq_from_paragraph(chunk)  # OK
#             parsed = parse_mcq_response(raw_response)  # OK
#     print(f"\n전체 요약 청크 수: {len(summary_chunks)}")

#     if not summary_chunks:
#         raise ValueError("요약된 내용이 없습니다.")

#     # 3. 요청 수보다 적으면 중복 허용
#     total_available = len(summary_chunks)
#     if total_available >= number_of_questions:
#         selected_chunks = random.sample(summary_chunks, number_of_questions)
#     else:
#         selected_chunks = summary_chunks * (number_of_questions // total_available)
#         selected_chunks += random.sample(summary_chunks, number_of_questions % total_available)

#     # 4. 각 청크에서 문제 생성
#     result = []
#     for chunk in selected_chunks:
#         raw = generate_mcq_from_paragraph(chunk)
#         parsed = parse_mcq_response(raw)
#         result.append(parsed)

#     return result  # [(question, choices, answer, explanation), ...]

# 11/ 04:12
# def generate_questions_from_summary_chunks(
#     chunks: List[Document],
#     number_of_questions: int
# ) -> List[Tuple[str, List[str], str, str]]:
#     # 1. 페이지별 텍스트 묶기
#     pages = defaultdict(list)
#     for chunk in chunks:
#         page = chunk.metadata.get("page", 0)
#         pages[page].append(chunk.page_content)

#     # 2. 페이지별 요약 + 요약 분할
#     summary_chunks = []
#     for page_num, texts in pages.items():
#         try:
#             summary = summarize_document(texts)  # texts는 List[str]
#             splits = split_summary_to_chunks(summary)
#             print(f"\n📄 페이지 {page_num} 요약:\n{summary}")
#             print(f"📄 페이지 {page_num} 요약 청크 {len(splits)}개:", splits)
#             summary_chunks.extend(splits)
#         except Exception as e:
#             print(f"⚠️ 페이지 {page_num} 요약 실패: {e}")

#     print(f"\n✅ 전체 요약 청크 수: {len(summary_chunks)}")

#     if not summary_chunks:
#         raise ValueError("요약된 내용이 없습니다.")

#     # 3. 생성할 문제 수만큼 청크 선택 (중복 허용)
#     total_available = len(summary_chunks)
#     if total_available >= number_of_questions:
#         selected_chunks = random.sample(summary_chunks, number_of_questions)
#     else:
#         if total_available == 0:
#             raise ValueError("사용 가능한 요약 청크가 없습니다.")
#         selected_chunks = summary_chunks * (number_of_questions // total_available)
#         selected_chunks += random.sample(summary_chunks, number_of_questions % total_available)

#     # 4. 각 청크에서 문제 생성
#     result = []
#     for i, chunk in enumerate(selected_chunks, start=1):
#         raw = generate_mcq_from_paragraph(chunk)
#         try:
#             parsed = parse_mcq_response(raw)
#             result.append(parsed)
#         except Exception as e:
#             print(f"\n⚠️ [{i}] 문제 파싱 실패: {e}\n응답 내용:\n{raw}\n")

#     return result  # [(question, choices, correct_answer, explanation)]

# 11 / 21:18

def generate_questions_from_summary_chunks(
    chunks: List[Document],
    number_of_questions: int
) -> List[Tuple[str, List[str], str, str]]:
    # ✅ 1. 'summary' 타입만 필터링
    summary_chunks = [
        chunk.page_content
        for chunk in chunks
        if chunk.metadata.get("type") == "summary"
    ]

    print(f"✅ 요약된 summary 청크 수: {len(summary_chunks)}")

    if not summary_chunks:
        raise ValueError("벡터 저장소에서 가져온 요약 데이터가 없습니다.")

    # ✅ 2. 필요한 수만큼 요약 청크 선택 (중복 허용)
    total_available = len(summary_chunks)
    if total_available >= number_of_questions:
        selected_chunks = random.sample(summary_chunks, number_of_questions)
    else:
        selected_chunks = summary_chunks * (number_of_questions // total_available)
        selected_chunks += random.sample(summary_chunks, number_of_questions % total_available)

    # ✅ 3. 객관식 문제 생성
    result = []
    for i, chunk in enumerate(selected_chunks, start=1):
        raw = generate_mcq_from_paragraph(chunk)
        try:
            parsed = parse_mcq_response(raw)
            result.append(parsed)
        except Exception as e:
            print(f"\n⚠️ [{i}] 문제 파싱 실패: {e}\n응답 내용:\n{raw}\n")

    return result
