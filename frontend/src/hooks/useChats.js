import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

export function useChats(topicId) {
  const [chats, setChats] = useState([])
  const { token } = useAuth()
  const backend = process.env.REACT_APP_BACKEND_URL

  useEffect(() => {
    if (!token || !topicId) return
    fetch(`${backend}/api/topics/${topicId}/chats`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setChats)
      .catch(console.error)
  }, [backend, token, topicId])

  return [chats, setChats]
}
