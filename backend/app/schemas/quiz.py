from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

class QuizBase(BaseModel):
    topic_id: int

class QuizCreate(QuizBase):
    document_ids: List[int]
    question_type: str  # 'ox' or 'mcq'
    number_of_questions: int

class Quiz(QuizBase):
    quiz_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str
    explanation: Optional[str] = None

class MCQQuestionCreate(QuizQuestionBase):
    choices: List[str]
    correct_answer: str

class OXQuestionCreate(QuizQuestionBase):
    correct_answer: bool

class QuizQuestion(QuizQuestionBase):
    question_id: int

    class Config:
        orm_mode = True

class QuizAttemptBase(BaseModel):
    user_id: Optional[int]

class QuizAttempt(QuizAttemptBase):
    attempt_id: int
    quiz_id: int
    attempted_at: datetime

    class Config:
        orm_mode = True

class QuizAnswerCreate(BaseModel):
    question_id: int
    user_answer: str

class QuizAnswer(QuizAnswerCreate):
    answer_id: int
    is_correct: bool

    class Config:
        orm_mode = True
        
class QuizAnswerRequest(BaseModel):
    questionId: int
    userAnswer: str  # "O", "X", "A", "B", ...

class QuizSubmitRequest(BaseModel):
    answers: List[QuizAnswerRequest]

class QuizResultItem(BaseModel):
    questionId: int
    question: str
    userAnswer: str
    correctAnswer: str
    isCorrect: bool
    explanation: Optional[str]

class QuizResultResponse(BaseModel):
    attemptId: int
    results: List[QuizResultItem]

class QuizListResponse(BaseModel):
    attemptId: int
    quizId: int
    createdAt: datetime
    questionCount: int
    
class QuizQuestionResponse(BaseModel):
    questionId:       int
    questionText:     str
    explanation:      Optional[str]
    questionType:     str       # "mcq" or "ox"
    choices:          Optional[List[str]]  # 객관식 보기, OX 면 None
    correctAnswer:    str
    userAnswer:       Optional[str]        # 내가 선택한 답

    class Config:
        orm_mode = True