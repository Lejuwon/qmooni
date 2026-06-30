// src/hooks/useQuizAttempts.js
import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'

export function useQuizAttempts() {
  const { token } = useAuth()
  const [attempts, setAttempts] = useState([])
  const [loading, setLoading]   = useState(false)

  const load = useCallback(async () => {
    if (!token) return
    setLoading(true)
    try {
      const res = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/quiz/list`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      if (!res.ok) throw new Error('이력 불러오기 실패')
      setAttempts(await res.json())
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    load()
    // 나중에 새 퀴즈 생성 시에도 갱신할 수 있게 이벤트 바인딩
    window.addEventListener('quizCreated', load)
    return () => window.removeEventListener('quizCreated', load)
  }, [load])

  return { attempts, loading, reload: load }
}
