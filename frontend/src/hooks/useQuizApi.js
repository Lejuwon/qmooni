// src/hooks/useQuizApi.js
import { useAuth } from '../context/AuthContext';
const BASE = process.env.REACT_APP_BACKEND_URL + '/api/quiz';

export function useQuizApi() {
  const { token } = useAuth();
  const headers = { 
    'Content-Type': 'application/json', 
    Authorization: `Bearer ${token}` 
  };

  /** 푼 퀴즈 목록 조회 */
  async function fetchAttempts() {
    const res = await fetch(`${BASE}/list`, { headers });
    if (!res.ok) throw new Error('퀴즈 목록 조회 실패');
    return res.json();
  }

  /** 새 퀴즈 생성 */
  async function generateQuiz({ topicId, documentId, type, numberOfQuestions }) {
    const res = await fetch(`${BASE}/generate`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        topicId,
        documentIds: [documentId],
        type,
        numberOfQuestions
      })
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`퀴즈 생성 실패: ${text}`);
    }
    return res.json(); // { quizId, attemptId, ... }
  }

  /** 퀴즈 문제 불러오기 (retry API 이용) */
  async function loadQuestions(attemptId, wrongOnly = false) {
    const res = await fetch(`${BASE}/retry/${attemptId}?wrongOnly=${wrongOnly}`, {
      method: 'POST',
      headers,
    });
    if (!res.ok) throw new Error('문제 불러오기 실패');
    return res.json(); // { newAttemptId, questions: [...] }
  }

  /** 퀴즈 제출 */
  async function submitQuiz(attemptId, answers) {
    const res = await fetch(`${BASE}/submit/${attemptId}`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ answers })
    });
    if (!res.ok) throw new Error('제출 실패');
    return res.json(); // { score, ... }
  }

  /** 결과 조회 */
  async function fetchResult(attemptId) {
    const res = await fetch(`${BASE}/result/${attemptId}`, { headers });
    if (!res.ok) throw new Error('결과 조회 실패');
    return res.json();
  }

  return {
    fetchAttempts,
    generateQuiz,
    loadQuestions,
    submitQuiz,
    fetchResult
  };
}
