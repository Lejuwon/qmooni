// src/components/ChatList.jsx
import React, { useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useChatSessions } from '../hooks/useChatSessions'

export default function ChatList({
  projectId,
  sessions = [],          // Sidebar에서 전달된 sessions
  activeSessionId,        // Sidebar에서 전달된 activeSessionId
}) {
  const navigate = useNavigate()

  // 이 프로젝트에 속한 세션만 필터링
  const filtered = sessions.filter(
    (s) => String(s.topic_id) === String(projectId)
  )

  if (filtered.length === 0) {
    return <p className="text-gray-400 italic">채팅이 없습니다.</p>
  }

  return (
    <ul className="space-y-1 overflow-auto max-h-[calc(100vh-10rem)]">
      {filtered.map((s) => {
        const isActive = String(s.session_id) === String(activeSessionId)
        return (
          <li
            key={s.session_id}
            onClick={() =>
              navigate(`/project/${projectId}/chat/${s.session_id}`)
            }
            className={`
              cursor-pointer px-4 py-2 rounded-lg transition-colors
              ${isActive
                ? 'bg-gray-200 font-medium'
                : 'bg-transparent hover:bg-gray-100'}
            `}
          >
            <div className="truncate">{s.title || '(제목 없음)'}</div>
          </li>
        )
      })}
    </ul>
  )
}

// // src/components/ChatList.jsx
// import React, { useEffect } from 'react'
// import { useNavigate, useParams } from 'react-router-dom'
// import { useChatSessions } from '../hooks/useChatSessions'

// export default function ChatList({ projectId, activeSessionId }) {
//   const navigate = useNavigate()
//   const { sessions, loading, reload } = useChatSessions()

//   useEffect(() => {
//     // 마운트 될 때 한 번, 그리고 sessionCreated 이벤트가 오면 다시 불러온다
//     reload()
//     window.addEventListener('sessionCreated', reload)
//     return () => window.removeEventListener('sessionCreated', reload)
//   }, [reload])

//   if (loading) return <p>세션 불러오는 중…</p>
//   if (!sessions.length) return <p className="text-gray-400 italic">채팅이 없습니다.</p>

//   return (
//     <ul className="space-y-2 overflow-auto max-h-[calc(100vh-10rem)]">
//       {sessions
//         .filter(s => String(s.topic_id) === projectId)
//         .map(s => {
//           const isActive = String(s.session_id) === activeSessionId
//           return (
//             <li
//               key={s.session_id}
//               onClick={() => navigate(`/project/${projectId}/chat/${s.session_id}`)}
//               className={`
//                 px-4 py-2 rounded-lg cursor-pointer transition-colors
//                 ${isActive
//                   ? 'bg-gray-200 font-medium'
//                   : 'bg-transparent hover:bg-gray-100'}
//               `}
//             >
//               <div className="truncate">{s.title || '(제목 없음)'}</div>
//             </li>
//           )
//         })}
//     </ul>
//   )
// }

