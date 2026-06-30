// src/pages/QuizPage.jsx
import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'    // ← pull in your context
import QmooniLayout from '../components/QmooniLayout'
import QuizList     from '../components/QuizList'

export default function QuizPage() {
  const { projectId } = useParams()
  const { token }     = useAuth()                 // ← get the current token
  const navigate      = useNavigate()

  const [docs, setDocs]             = useState([])
  const [loadingDocs, setLoading]   = useState(true)
  const [selectedDoc, setSelected]  = useState(null)
  const [count, setCount]           = useState(5)
  const [format, setFormat]         = useState('OX')

  useEffect(() => {
    setLoading(true)
    fetch(
      `${process.env.REACT_APP_BACKEND_URL}/api/topics/${projectId}/documents`,
      { headers: { Authorization: `Bearer ${token}` } }
    )
      .then(res => {
        if (res.status === 401) {
          // not logged in / token expired
          navigate('/')
          return Promise.reject('unauthorized')
        }
        if (!res.ok) {
          return Promise.reject(res.statusText)
        }
        return res.json()
      })
      .then(docs => setDocs(docs))
      .catch(err => console.error('could not load documents', err))
      .finally(() => setLoading(false))
  }, [projectId, token, navigate])

  // 문제 생성 후 퀴즈 화면으로 이동 
  const handleStart = async () => {
    if (!selectedDoc) {
      alert('문서를 선택해주세요.')
      return
    }

    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/quiz/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({
        topicId: +projectId,
        documentIds: [selectedDoc.document_id],
        type: format === 'MC' ? 'mcq' : 'ox',          // 'ox' 또는 'mcq'
        numberOfQuestions: count
      })
    })
    .then(async res => {
      if (!res.ok) {
        // 에러 바디를 JSON으로 파싱
        const err = await res.json()
        throw err
      }
      return res.json()
    })
    .then(data => {
      // 생성 성공 시 data에 attemptId, quizId 등이 들어옵니다.
      console.log('퀴즈 생성 성공:', data)
      // TODO: QuizWindow 등으로 화면 전환
      navigate(`/project/${projectId}/quiz/${data.attemptId}`)
    })
    .catch(err => {
      // detail.join 에러 나던 부분을 고쳤습니다
      const d = err.detail
      const msg = Array.isArray(d) ? d.join('\n') : d
      alert(`퀴즈 생성 중 오류가 발생했습니다:\n${msg}`)
    })
  }
    
  return (
    <QmooniLayout>
      <div className="flex-1 flex overflow-hidden mt-12">
        {/* 좌측: 업로드된 문서 리스트 */}
        <aside className="w-1/4 p-4 overflow-auto">
          <div className="bg-white rounded-xl shadow p-4 h-full flex flex-col">
            <h2 className="text-xl font-semibold mb-4">문서 선택</h2>
            {loadingDocs
              ? <p className="text-gray-500">불러오는 중…</p>
              : docs.length
                ? (
                  <ul className="space-y-3">
                    {docs.map(doc => (
                      <li
                        key={doc.document_id}
                        onClick={() => setSelected(doc)}
                        className={`cursor-pointer px-4 py-2 rounded-lg transition ${
                          selectedDoc?.document_id === doc.document_id
                            ? 'bg-orange-50 border-l-4 border-orange-100 font-medium'
                            : 'hover:bg-gray-100'
                        }`}
                      >
                      {doc.file_name}
                      </li>
                    ))}
                  </ul>
                )
                : <p className="italic text-gray-400">문서가 없습니다.</p>
            }
          </div>
        </aside>

        {/* 우측: 옵션 및 START */}
        <main className="flex-1 p-4 overflow-auto flex justify-center items-start">
          <div className="w-full max-w-3xl mx-auto bg-white shadow-lg rounded-xl p-10 space-y-6 h-full">
            <h1 className="text-2xl font-bold mb-6 text-center">주제 퀴즈 만들기</h1>

            <div className="mb-6">
              <span className="block text-gray-700 mb-2">선택된 문서</span>
              <div className="px-4 py-3 bg-gray-50 rounded-lg border">
                {selectedDoc?.file_name || <span className="text-gray-400">없음</span>}
              </div>
            </div>

            <div className="mb-6 text-center">
              <p className="text-gray-700 mb-2">문제 수</p>
              <div className="inline-flex space-x-3">
                {[5, 10, 15, 20].map(n => (
                  <button
                    key={n}
                    onClick={() => setCount(n)}
                    className={`px-4 py-2 rounded-lg transition ${
                      count === n ? 'bg-orange-500 text-white shadow' : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>

            <div className="mb-8 text-center">
              <p className="text-gray-700 mb-2">형식</p>
              <div className="inline-flex space-x-3">
                {['OX', 'MC'].map(f => (
                  <button
                    key={f}
                    onClick={() => setFormat(f)}
                    className={`px-4 py-2 rounded-lg transition ${
                      format === f ? 'bg-orange-500 text-white shadow' : 'bg-gray-200 hover:bg-gray-300'
                    }`}
                  >
                    {f === 'OX' ? 'O/X' : '객관식'}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleStart}
              className="w-full py-3 bg-orange-500 text-white rounded-full font-semibold hover:bg-orange-600 transition-shadow shadow-md"
            >
              START
            </button>
          </div>
        </main>
      </div>
    </QmooniLayout>
  )
}
