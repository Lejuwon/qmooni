// src/pages/QuizResultPage.jsx
import React, { useState, useEffect } from 'react'
import { useParams, useNavigate }     from 'react-router-dom'
import { useAuth }                    from '../context/AuthContext'
import QmooniLayout                   from '../components/QmooniLayout'

export default function QuizResultPage() {
  const { token }       = useAuth()
  const { projectId, attemptId } = useParams()
  const navigate        = useNavigate()
  const [result, setResult]   = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(
      `${process.env.REACT_APP_BACKEND_URL}/api/quiz/result/${attemptId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    )
      .then(r => r.ok ? r.json() : Promise.reject('불러오기 실패'))
      .then(data => setResult(data))
      .catch(err => { alert('결과 로드 중 오류'); console.error(err) })
      .finally(() => setLoading(false))
  }, [attemptId, token])

  // 2) 재도전 핸들러
  const handleRetry = async (wrongOnly) => {
    try {
      const res = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/quiz/retry/${attemptId}?wrongOnly=${wrongOnly}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          }
        }
      )
      if (!res.ok) {
        const err = await res.json()
        alert(err.detail || '재도전 생성 실패')
        return
      }
      const { newAttemptId, questions } = await res.json()

      console.log('New attempt ID:', newAttemptId);
      console.log('Questions:', questions);

      // 틀린 문제만 재도전인데, questions가 비어 있으면 경고 후 종료
      if (wrongOnly && questions.length === 0) {
        alert('틀린 문제가 없습니다!')
        return
      }

      // 사이드바에 새 이력 갱신 이벤트
      window.dispatchEvent(new CustomEvent('quizCreated'))

      // 새 풀기 화면으로 이동
    //   navigate(`/project/${projectId}/quiz/${newAttemptId}`)
      navigate(
        `/project/${projectId}/quiz/${newAttemptId}`,
        { state: { initialQuestions: questions } }
        )
    } catch (e) {
      console.error(e)
      alert('재도전 중 오류가 발생했습니다.')
    }
  }

  if (loading) return <p className="p-6">결과를 불러오는 중…</p>
  if (!result) return <p className="p-6 text-red-500">결과가 없습니다.</p>

  const correctCount = result.results.filter(r => r.isCorrect).length
  const totalCount   = result.results.length

  return (
    <QmooniLayout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-bold">퀴즈 결과</h1>
        <div className="text-xl">
          점수: <span className="font-semibold">{correctCount}</span> / {totalCount}
        </div>

        <div className="space-x-3">
          <button
            onClick={() => navigate(`/project/${projectId}/quiz`)}
            className="px-4 py-2 bg-gray-100 rounded hover:bg-gray-300"
          >
            퀴즈 페이지로
          </button>
          <button
            onClick={() => handleRetry(false)}
            className="px-4 py-2 bg-orange-50 rounded hover:bg-orange-200"
          >
            전체 다시 풀기
          </button>
          <button
            onClick={() => handleRetry(true)}
            className="px-4 py-2 bg-orange-100 rounded hover:bg-orange-300"
          >
            틀린 문제만 다시 풀기
          </button>
        </div>

        <hr />

        <h2 className="text-lg font-medium">풀이 보기</h2>
        <ul className="space-y-4">
          {result.results.map((q, idx) => (
            <li key={q.questionId} className="p-4 border rounded">
              <p className="font-medium">{idx + 1}. {q.question}</p>
              <p className={`mt-2 ${q.isCorrect ? 'text-green-600' : 'text-red-600'}`}>
                내 답: <strong>{q.userAnswer}</strong> / 정답: <strong>{q.correctAnswer}</strong>
              </p>
              {q.explanation && (
                <p className="mt-2 text-gray-700">해설: {q.explanation}</p>
              )}
            </li>
          ))}
        </ul>
      </div>
    </QmooniLayout>
  )
}
