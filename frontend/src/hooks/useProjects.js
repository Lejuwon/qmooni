import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

export function useProjects() {
  const [projects, setProjects] = useState([])
  const { token } = useAuth()
  const backend = process.env.REACT_APP_BACKEND_URL

  useEffect(() => {
    if (!token) return
    fetch(`${backend}/api/topics`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setProjects)
      .catch(console.error)
  }, [backend, token])

  return [projects, setProjects]
}
