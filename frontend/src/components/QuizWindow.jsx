// src/components/QuizWindow.jsx
import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import QmooniLayout from './QmooniLayout'

export default function QuizWindow() {
  const { token }      = useAuth()
  const { attemptId, projectId }  = useParams()
  const navigate      = useNavigate()
  const { state }      = useLocation()
  // 1) state 초기 질문이 있으면 그대로 쓰고, 없으면 빈 배열
  const [questions, setQuestions] = useState([])
  // 2) initialQuestions 가 없으면 로딩 표시
  const [loading, setLoading]     = useState(true)
  const [answers, setAnswers]     = useState({})

  // useEffect(() => {
  //   console.log('Initial state:', state);
  //   // state.initialQuestions 가 있으면 GET 호출 스킵
  //   if (state?.initialQuestions) return

  //   fetch(`${process.env.REACT_APP_BACKEND_URL}/api/quiz/attempt/${attemptId}/questions`, {
  //     headers: {
  //       'Content-Type': 'application/json',
  //       Authorization: `Bearer ${token}`,
  //     }
  //   })
  //     .then(r => {
  //       if (!r.ok) throw new Error('질문 로드 실패')
  //       return r.json()
  //     })
  //     .then(qs => {
  //       setQuestions(qs)
  //       setLoading(false)
  //     })
  //     .catch(err => {
  //       console.error("문제 로딩 실패", err);
  //       alert("문제 로딩 중 오류가 발생했습니다.");
  //     })
  // }, [attemptId, token, state])
  useEffect(() => {
    console.log('Initial state:', state);
    // state.initialQuestions 가 있으면 GET 호출 스킵
    // if (state?.initialQuestions) {
    //   const ids = state.initialQuestions.map(q => q.questionId)}

    setLoading(true)

    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/quiz/attempt/${attemptId}/questions`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      }
    })
      .then(r => {
        if (!r.ok) throw new Error('질문 로드 실패')
        return r.json()
      })
      .then(qs => {
        setQuestions(qs)
        setLoading(false)
      })
      .catch(err => {
        console.error("문제 로딩 실패", err);
        alert("문제 로딩 중 오류가 발생했습니다.");
      })
  }, [attemptId, token])

  // 추가: 상태가 바뀔 때 다시 렌더링 강제
  // useEffect(() => {
  //   setQuestions(state?.initialQuestions || []);
  // }, [state?.initialQuestions]);

  if (loading) return <p>문제를 불러오는 중…</p>
  if (!questions.length) return <p>표출할 문제가 없습니다.</p>

  // 2) 답안 선택 핸들러
  const handleChange = (qid, value) =>
    setAnswers(prev => ({ ...prev, [qid]: value }))

  // 3) 제출 & 결과 보기로 이동
  const handleSubmit = async () => {
    const payload = {
      answers: questions.map(q => ({
        questionId:    q.questionId,
        userAnswer:    answers[q.questionId] || ''
      }))
    }

    const res = await fetch(
      `${process.env.REACT_APP_BACKEND_URL}/api/quiz/submit/${attemptId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload),
      }
    )
    if (!res.ok) {
      const err = await res.json()
      const msg = err.detail || '제출에 실패했습니다.'
      alert(msg)
      return
    }
    // 성공하면 결과 페이지로 이동
    navigate(`/project/${projectId}/quiz/${attemptId}/result`)
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h2 className="text-2xl font-bold text-center mb-8">퀴즈 풀기</h2>
      {questions.map(q => (
        <div key={q.questionId} className="bg-white rounded-lg shadow p-6 mb-6">
          <p className="font-medium mb-4">{q.questionText}</p>

          <div className="mt-4 flex justify-center space-x-12">
            {q.questionType === 'ox' ? (
              ['O','X'].map(o => (
                <label key={o} className="flex items-center space-x-2">
                  <input
                    type="radio"
                    className="w-6 h-6"
                    name={`q-${q.questionId}`}
                    value={o}
                    checked={answers[q.questionId] === o}
                    onChange={() => handleChange(q.questionId, o)}
                  />
                  <span className="text-xl font-semibold">{o}</span>
                </label>
              ))
            ) : (
              q.choices.map(c => (
                <label key={c} className="flex items-center space-x-2">
                  <input
                    type="radio"
                    className="w-6 h-6"
                    name={`q-${q.questionId}`}
                    value={c}
                    checked={answers[q.questionId] === c}
                    onChange={() => handleChange(q.questionId, c)}
                  />
                  <span className="text-base">{c}</span>
                </label>
              ))
            )}
          </div>
        </div>
      ))}

      <button
        onClick={handleSubmit}
        className="w-full py-3 bg-orange-600 hover:bg-orange-700 text-white font-semibold rounded-lg transition"
      >
        제출하기
      </button>
    </div>
  )
}