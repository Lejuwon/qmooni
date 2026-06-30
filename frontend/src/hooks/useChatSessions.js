// src/hooks/useChatSessions.js
import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'

export function useChatSessions() {
  const { token } = useAuth()
  const backend = process.env.REACT_APP_BACKEND_URL
  const [sessions, setSessions] = useState([])

  const loadSessions = useCallback(async () => {
    if (!token) return
    const res = await fetch(`${backend}/api/chat/sessions`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) setSessions(await res.json())
  }, [token, backend])

  // **한 번만** 실행
  useEffect(() => {
    loadSessions()
  }, [loadSessions])

  return { sessions, reload: loadSessions, loading: !sessions.length }
}

// // src/hooks/useChatSessions.js
// import { useState, useEffect } from 'react';
// import { useAuth } from '../context/AuthContext';

// export function useChatSessions() {
//   const { token } = useAuth();
//   const [sessions, setSessions] = useState([]);

//   const loadSessions = async () => {
//     const res = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/chat/sessions`, {
//       headers: { Authorization: `Bearer ${token}` },
//     });
//     if (res.ok) setSessions(await res.json());
//   };

//   useEffect(() => { if (token) loadSessions(); }, [token]);

//   return { sessions, reload: loadSessions };
// }
