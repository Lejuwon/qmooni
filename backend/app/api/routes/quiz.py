from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.vectorstore.chunk_fetcher import get_chunks_from_documents
from app.models.quiz import Quiz, QuizQuestion, MCQQuestion, OXQuestion, QuizAttempt, QuizAnswer
from app.schemas.quiz import QuizListResponse, QuizQuestionResponse, QuizSubmitRequest, QuizResultResponse  # 예시 모델들
from app.models.document import Document
from app.models.quiz import Quiz, QuizAttempt
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.api.deps import get_current_user_id
import os

router = APIRouter(tags=["quiz"])

class QuizGenerateRequest(BaseModel):
    topicId: int
    documentIds: List[int]
    type: str  # "mcq" 또는 "ox"
    numberOfQuestions: int

    class Config:
        allow_population_by_field_name = True

# 퀴즈 생성성
@router.post("/generate")
def generate_quiz(request: QuizGenerateRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    if request.type not in {"mcq", "ox"}:
        raise HTTPException(status_code=400, detail="지원되지 않는 문제 유형입니다.")

    # 단일 문서만 허용
    if len(request.documentIds) != 1:
        raise HTTPException(status_code=400, detail="퀴즈는 하나의 문서에 대해서만 생성할 수 있습니다.")
    document_id = request.documentIds[0]

    # 문서에서 chunk 추출
    chunks = get_chunks_from_documents(
        user_topic_id=request.topicId,
        document_ids=request.documentIds,
        db=db
    )

    if not chunks:
        raise HTTPException(status_code=404, detail="문서에서 추출된 텍스트가 없습니다.")

    try:
        if request.type == "mcq":
            from app.services.quiz_generator_mcq import generate_questions_from_summary_chunks
            questions = generate_questions_from_summary_chunks(
                chunks=chunks,
                number_of_questions=request.numberOfQuestions
            )
        elif request.type == "ox":
            from app.services.quiz_generator_ox import generate_ox_questions_from_summary_chunks
            questions = generate_ox_questions_from_summary_chunks(
                chunks=chunks,
                number_of_questions=request.numberOfQuestions
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"문제 생성 실패: {e}")

    if not questions:
        raise HTTPException(status_code=500, detail="문제가 생성되지 않았습니다.")

    # 퀴즈 저장 (document_id 포함)
    quiz = Quiz(
        topic_id=request.topicId,
        document_id=document_id
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    # 퀴즈 질문과 보기 저장
    for question_data in questions:
        if request.type == "mcq":
            question_text, choices, correct_answer, explanation = question_data
            question = QuizQuestion(
                quiz_id=quiz.quiz_id,
                question_type="mcq",
                question_text=question_text,
                explanation=explanation
            )
            db.add(question)
            db.flush()
            db.refresh(question)

            mcq = MCQQuestion(
                question_id=question.question_id,
                choices=choices,
                correct_answer=correct_answer
            )
            db.add(mcq)

        elif request.type == "ox":
            question_text, ox_answer, explanation = question_data
            question = QuizQuestion(
                quiz_id=quiz.quiz_id,
                question_type="ox",
                question_text=question_text,
                explanation=explanation
            )
            db.add(question)
            db.flush()
            db.refresh(question)

            ox = OXQuestion(
                question_id=question.question_id,
                correct_answer=ox_answer
            )
            db.add(ox)

    # 첫 번째 시도 자동 생성
    attempt = QuizAttempt(
        quiz_id=quiz.quiz_id,
        user_id=user_id
    )
    db.add(attempt)

    db.commit()
    db.refresh(attempt)

    return {
        "quizId": quiz.quiz_id,
        "quizType": request.type,
        "numberOfQuestions": len(questions),
        "attemptId": attempt.attempt_id,
        "message": "퀴즈가 성공적으로 생성되었습니다."
    }

# 질문과 보기 조회   
@router.get(
    "/attempt/{attempt_id}/questions",
    response_model=List[QuizQuestionResponse]
)
def get_attempt_questions(
    attempt_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    # 1) 시도 자체가 내 것인지 확인
    attempt = (
        db.query(QuizAttempt)
          .filter_by(attempt_id=attempt_id, user_id=user_id)
          .first()
    )
    if not attempt:
        raise HTTPException(404, "해당 시도 기록이 없습니다.")

    # 2) 문제 목록 순회하며 보기와 내 답 함께 조회
    questions = []
    qs = db.query(QuizQuestion).filter_by(quiz_id=attempt.quiz_id).all()
    for q in qs:
        # 내 답
        ans = (
            db.query(QuizAnswer)
              .filter_by(attempt_id=attempt_id, question_id=q.question_id)
              .first()
        )
        # 기본 필드 채우기
        item = {
            "questionId":       q.question_id,
            "questionText":     q.question_text,
            "explanation":      q.explanation,
            "questionType":     q.question_type,
            "choices":          None,
            "correctAnswer":    None,
            "userAnswer":       ans.user_answer if ans else None,
        }

        if q.question_type == "mcq":
            mc = (
                db.query(MCQQuestion)
                  .filter_by(question_id=q.question_id)
                  .first()
            )
            item["choices"] = mc.choices
            item["correctAnswer"] = mc.correct_answer
        else:  # OX 문제
            ox = (
                db.query(OXQuestion)
                  .filter_by(question_id=q.question_id)
                  .first()
            )
            item["correctAnswer"] = "O" if ox.correct_answer else "X"

        questions.append(item)

    return questions

# 퀴즈 제출
@router.post("/submit/{attempt_id}")
def submit_quiz(attempt_id: int, request: QuizSubmitRequest, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    attempt = db.query(QuizAttempt).filter_by(attempt_id=attempt_id, user_id=user_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="존재하지 않는 시도입니다.")

    existing_answers = db.query(QuizAnswer).filter_by(attempt_id=attempt_id).first()
    if existing_answers:
        raise HTTPException(status_code=400, detail="이미 제출된 시도입니다.")

    correct_count = 0
    for answer in request.answers:
        question = db.query(QuizQuestion).filter_by(question_id=answer.questionId).first()
        if not question:
            continue

        correct = False
        if question.question_type == "mcq":
            correct_answer = db.query(MCQQuestion).filter_by(question_id=question.question_id).first().correct_answer
            correct = (answer.userAnswer == correct_answer)
        elif question.question_type == "ox":
            correct_answer = db.query(OXQuestion).filter_by(question_id=question.question_id).first().correct_answer
            correct = (answer.userAnswer == correct_answer)

        if correct:
            correct_count += 1

        db.add(QuizAnswer(
            attempt_id=attempt.attempt_id,
            question_id=question.question_id,
            user_answer=answer.userAnswer,
            is_correct=correct
        ))

    db.commit()

    return {"attemptId": attempt.attempt_id, "score": correct_count, "message": "퀴즈 제출 완료"}


# 퀴즈 결과 조회
@router.get("/result/{attempt_id}", response_model=QuizResultResponse)
def get_result(attempt_id: int, db: Session = Depends(get_db)):
    answers = db.query(QuizAnswer).filter_by(attempt_id=attempt_id).all()
    if not answers:
        raise HTTPException(status_code=404, detail="제출 결과가 없습니다.")

    result = []
    for ans in answers:
        question = db.query(QuizQuestion).filter_by(question_id=ans.question_id).first()
        result.append({
            "questionId": question.question_id,
            "question": question.question_text,
            "userAnswer": ans.user_answer,
            "correctAnswer": db.query(MCQQuestion if question.question_type == "mcq" else OXQuestion)
                                    .filter_by(question_id=question.question_id).first().correct_answer,
            "isCorrect": ans.is_correct,
            "explanation": question.explanation
        })

    return {"attemptId": attempt_id, "results": result}


# 퀴즈 시도 목록 조회 - 사이드바
@router.get("/list")
def get_quiz_list(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    attempts = (
        db.query(QuizAttempt)
        .join(Quiz, Quiz.quiz_id == QuizAttempt.quiz_id)
        .filter(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.attempted_at.desc())
        .all()
    )

    result = []
    for a in attempts:
        quiz = db.query(Quiz).filter_by(quiz_id=a.quiz_id).first()

        # 문제 유형 추론 (첫 문제의 question_type 사용)
        first_question = (
            db.query(QuizQuestion)
            .filter_by(quiz_id=quiz.quiz_id)
            .order_by(QuizQuestion.question_id.asc())
            .first()
        )
        quiz_type = first_question.question_type if first_question else "unknown"
        quiz_type_label = "[사지선다]" if quiz_type == "mcq" else "[OX]" if quiz_type == "ox" else "[알수없음]"

        # ✅ 단일 document_id 기반 문서명 조회
        doc = db.query(Document).filter_by(document_id=quiz.document_id).first()
        doc_title = os.path.splitext(doc.file_name)[0] if doc else "문서 없음"

        attempt_title = f"{quiz_type_label} {doc_title}"

        # ✅ 정답 수 카운트
        answer_count = db.query(QuizAnswer).filter_by(attempt_id=a.attempt_id).count()

        result.append({
            "attemptId": a.attempt_id,
            "quizId": a.quiz_id,
            "createdAt": a.attempted_at,
            "questionCount": answer_count,
            "attemptTitle": attempt_title
        })

    return result


# 다시 풀기 (전체 또는 틀린 문제만)
@router.post("/retry/{attempt_id}")
def retry_quiz(
    attempt_id: int,
    wrongOnly: bool = True,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    old_answers = db.query(QuizAnswer).filter_by(attempt_id=attempt_id).all()
    if not old_answers:
        raise HTTPException(status_code=404, detail="기존 시도가 없습니다.")

    old_attempt = db.query(QuizAttempt).filter_by(attempt_id=attempt_id).first()
    quiz = db.query(Quiz).filter_by(quiz_id=old_attempt.quiz_id).first()

    # 새로운 attempt 생성
    new_attempt = QuizAttempt(
        quiz_id=quiz.quiz_id,
        user_id=user_id,
        attempted_at=datetime.utcnow()
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    # 기존 문제 중 틀린 문제만 or 전체 문제 ID 추출
    question_ids = [a.question_id for a in old_answers if not a.is_correct] if wrongOnly else [a.question_id for a in old_answers]

    # 문제 정보 구성
    questions_response = []
    for qid in question_ids:
        question = db.query(QuizQuestion).filter_by(question_id=qid).first()
        if not question:
            continue

        q_data = {
            "questionId": question.question_id,
            "question": question.question_text,
            "questionType": question.question_type,
        }

        if question.question_type == "mcq":
            mcq = db.query(MCQQuestion).filter_by(question_id=qid).first()
            q_data["choices"] = mcq.choices if mcq else []
        elif question.question_type == "ox":
            q_data["choices"] = ["O", "X"]

        questions_response.append(q_data)

    return {
        "newAttemptId": new_attempt.attempt_id,
        "questions": questions_response,
        "message": "다시 풀기 세션이 생성되었습니다."
    }