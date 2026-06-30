// src/pages/ChatPage.jsx
import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import QmooniLayout             from '../components/QmooniLayout'
import ChatList                 from '../components/ChatList'
import ChatWindow               from '../components/ChatWindow'
import { useChatSessions }      from '../hooks/useChatSessions'

export default function ChatPage() {
  const { projectId, sessionId: routeSid } = useParams()
  const { sessions, reload }               = useChatSessions()
  const [sessionId, setSessionId]          = useState(routeSid)
  const navigate = useNavigate();

  useEffect(() => {
    setSessionId(routeSid)
  }, [routeSid])

  const handleNewSession = (newSid) => {
    setSessionId(newSid)
    reload()
  }

  return (
    <QmooniLayout>
      {/* 본문은 오직 ChatWindow 만 */}
      <div className="flex-1 flex flex-col">
        <ChatWindow
          key={sessionId ?? 'new'}
          topicId={projectId}
          sessionId={sessionId}
          onNewSession={(newId) => {
            // navigate(`/project/${projectId}/chat/${newId}`)

            // 예: URL 파라미터 바꾸기
            window.history.replaceState(
              null,
              '',
              `/project/${projectId}/chat/${newId}`);
            window.dispatchEvent(new Event('sessionCreated'))
          }}
        />
      </div>

    </QmooniLayout>
  )
}

