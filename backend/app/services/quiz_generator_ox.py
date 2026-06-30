import os
import re
import random
from typing import List, Tuple
from openai import OpenAI
from langchain.schema import Document
from dotenv import load_dotenv

# 환경변수 로딩 (OPENAI_API_KEY)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_ox_from_paragraph(paragraph: str) -> str:
    """
    주어진 문단/문장을 기반으로 OX 문제를 생성합니다.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 한국어 OX 퀴즈를 만드는 AI야. 다음 문단을 기반으로 사실인지 여부를 묻는 문제를 만들어.\n\n"
                        "다음 지침을 반드시 따라:\n"
                        "1. 문제는 문단 없이도 의미가 명확하게 전달되어야 해. '이 문서', '이 문장', '위 문단' 같은 표현은 절대 쓰지 마.\n"
                        "예: (X) '문서에는 목표달성 과정에 대한 내용이 포함되어 있다.'\n(O) '목표달성 과정은 조직이 설정한 전략을 기반으로 추진된다.'"
                        "2. 항상 정답이 'O'가 되지 않도록 해. 혼동하기 쉬운 개념이나 자주 착각하는 내용을 활용해 일부 문제는 정답이 'X'가 되도록 해.\n"
                        "3. 질문은 간결하고 명확하게 작성할 것.\n"
                        "4. 해설은 왜 맞거나 틀린지를 간단하고 논리적으로 설명할 것. 보기의 순서를 기준으로 정답을 언급하지 마.\n\n"
                        "다음은 좋은 질문의 예시야:\n"
                        "질문: 델파이 기법은 정교한 계량 모형을 기반으로 한다.\n"
                        "정답: X\n"
                        "해설: 델파이 기법은 전문가의 의견을 수렴하는 방식이며, 계량 모형과는 관련이 없다.\n\n"
                        "형식:\n"
                        "질문: ...\n"
                        "정답: O 또는 X\n"
                        "해설: ..."
                    )
                },
                {
                    "role": "user",
                    "content": f"다음 문단을 기반으로 OX 문제를 만들어줘:\n\n{paragraph}"
                }
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"OX 문제 생성 실패: {str(e)}"


def parse_ox_response(response: str) -> Tuple[str, str, str]:
    """
    OX 생성 응답 텍스트에서 질문, 정답(O/X), 해설을 추출합니다.
    """
    lines = response.strip().splitlines()
    question = ""
    answer = ""
    explanation = ""

    for line in lines:
        if line.startswith("질문:"):
            question = line.replace("질문:", "").strip()
        elif line.startswith("정답:"):
            match = re.search(r"\b[OX]\b", line.upper())
            if match:
                answer = match.group(0)
            else:
                raise ValueError("정답 형식 오류")
        elif line.startswith("해설:"):
            explanation = line.replace("해설:", "").strip()

    if not question or not answer:
        raise ValueError("질문 또는 정답이 비어 있음")

    return question, answer, explanation


def generate_ox_questions_from_summary_chunks(
    chunks: List[Document],
    number_of_questions: int
) -> List[Tuple[str, str, str]]:
    """
    요약 청크 목록으로부터 OX 문제들을 생성합니다.
    각 문제는 (질문, 정답("O"/"X"), 해설)로 구성됩니다.
    """
    summary_chunks = [
        chunk.page_content
        for chunk in chunks
        if chunk.metadata.get("type") == "summary"
    ]

    if not summary_chunks:
        raise ValueError("요약 청크가 없습니다.")

    total = len(summary_chunks)
    selected = (
        random.sample(summary_chunks, number_of_questions)
        if total >= number_of_questions else
        summary_chunks * (number_of_questions // total) +
        random.sample(summary_chunks, number_of_questions % total)
    )

    results = []
    for i, chunk in enumerate(selected, 1):
        raw = generate_ox_from_paragraph(chunk)
        try:
            parsed = parse_ox_response(raw)
            results.append(parsed)
        except Exception as e:
            print(f"\n⚠️ [{i}] OX 파싱 실패: {e}\n응답:\n{raw}\n")

    return results