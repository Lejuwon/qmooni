// src/components/Sidebar.jsx
import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation, useParams } from 'react-router-dom'
import { Menu } from 'lucide-react'
import { useTopics } from '../hooks/useTopics'
import { useChatSessions } from '../hooks/useChatSessions'
// import { useQuizAttempts } from '../hooks/useQuizAttempts'
import { useAuth } from '../context/AuthContext'
import quizIcon from '../assets/quizIcon.png'
import chatbotIcon from '../assets/chatbotIcon.png'
import ChatList from './ChatList'
import ProjectList from './ProjectList'
import QuizList from './QuizList'

export default function Sidebar() {
  const { token } = useAuth()
  const { topics, loading: topicsLoading, create, update, remove } = useTopics()
  const { sessions, reload: reloadSessions, loading: sessionsLoading } = useChatSessions()
  // const { attempts, loading: attemptsLoading, reload: reloadAttempts } = useQuizAttempts()
  // const { quizSessions, reload: reloadQuizSessions, loading: quizLoading } = useQuizSessions()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const navigate = useNavigate()
  const location = useLocation()
  const { projectId, sessionId } = useParams()

  const isProjectPage = Boolean(projectId)
  const isChatPage    = isProjectPage && location.pathname.includes('/chat')
  const isQuizPage    = isProjectPage && location.pathname.includes('/quiz')

  // const activeSession = sessions.find(s => String(s.session_id) === String(sessionId))

  useEffect(() => {
    // 세션 생성 시 sidebar 에서도 다시 불러오기
    window.addEventListener('sessionCreated', reloadSessions)
    return () => window.removeEventListener('sessionCreated', reloadSessions)
  }, [reloadSessions])

  // 상단 토글 버튼: 프로젝트 내부에서만 보임
  function TopToggleButton() {
    if (!isProjectPage || !sidebarOpen) return null

    return (
      <button
        onClick={() => {
          // 챗화면이면 퀴즈로, 아니면 챗으로
          if (isChatPage) navigate(`/project/${projectId}/quiz`)
          else               navigate(`/project/${projectId}/chat`)
        }}
        className="flex items-center mb-6 px-3 py-2 bg-white rounded-lg shadow hover:bg-gray-50"
      >
        <img
          src={isChatPage ? quizIcon : chatbotIcon}
          alt={isChatPage ? '퀴즈' : '챗봇'}
          className="w-5 h-5 mr-2"
        />
        <span className="text-sm font-medium">
          {isChatPage ? '퀴즈' : '챗봇'}
        </span>
      </button>
    )
  }

  // + 새 대화 버튼: 채팅 화면일 때만
  function NewSessionButton() {
    if (!isChatPage || !sidebarOpen) return null

    return (
      <button
        onClick={async () => {
          navigate(`/project/${projectId}/chat`)         
          // await reloadSessions()          
        }}
        className="flex items-center mb-4 px-3 py-2 rounded-lg hover:bg-gray-200 text-gray-700"
      >
        <span className="text-xl mr-2">＋</span>
        <span>새 대화</span>
      </button>
    )
  }

  return (
    <aside
      className={`
        flex-shrink-0 h-full flex flex-col
        bg-[#fcf7ef] border-r border-gray-200
        transition-all duration-300
        ${sidebarOpen ? 'w-64' : 'w-14'}
      `}
    >
      <div className="p-4 flex flex-col">
        {/* 햄버거 아이콘 */}
        <button
          onClick={() => setSidebarOpen(o => !o)}
          className="p-2 rounded hover:bg-gray-100 mb-4"
        >
          <Menu size={24} />
        </button>

        <TopToggleButton />
        <NewSessionButton />

        {sidebarOpen && (
          isProjectPage
            ? (
              isChatPage
                // 채팅 화면 → ChatList 렌더
                ? sessionsLoading
                  ? <p>세션 불러오는 중…</p>
                  : (
                    <ChatList
                      projectId={projectId}
                      // sessions={sessions}
                      // activeSessionId={sessionId}
                      sessions={sessions.filter(s => s.topic_id === +projectId)}
                      activeSessionId={+sessionId}
                    />
                  )
              // 퀴즈 화면: QuizList
              : isQuizPage
                ? <QuizList projectId={projectId} />    
                // 프로젝트 상세(파일 업로드) 화면 → 그냥 프로젝트 목록 유지
                : topicsLoading
                  ? <p>프로젝트 불러오는 중…</p>
                  : (
                    <ProjectList
                      projects={topics}
                      activeProjectId={+projectId}
                      onAdd={async () => {
                        const title = prompt('새 프로젝트 이름을 입력하세요')
                        if (title) await create(title).catch(console.error)
                      }}
                      onClick={p => navigate(`/project/${p.topic_id}`)}
                      onRename={async p => {
                        const title = prompt('새 프로젝트 이름', p.title)
                        if (title) await update(p.topic_id, title).catch(console.error)
                      }}
                      onDelete={async p => {
                        if (window.confirm(`"${p.title}" 프로젝트를 삭제하시겠습니까?`)) {
                          await remove(p.topic_id).catch(console.error)
                        }
                      }}
                    />
                  )
            )
            // 홈(로그인 후) → 프로젝트 목록
            : topicsLoading
              ? <p>프로젝트 불러오는 중…</p>
              : (
                <ProjectList
                  projects={topics}
                  onAdd={async () => {
                    const title = prompt('새 프로젝트 이름을 입력하세요')
                    if (title) await create(title).catch(console.error)
                  }}
                  onClick={p => navigate(`/project/${p.topic_id}`)}
                  onRename={async p => {
                    const title = prompt('새 프로젝트 이름', p.title)
                    if (title) await update(p.topic_id, title).catch(console.error)
                  }}
                  onDelete={async p => {
                    if (window.confirm(`"${p.title}" 프로젝트를 삭제하시겠습니까?`)) {
                      await remove(p.topic_id).catch(console.error)
                    }
                  }}
                />
              )
        )}
      </div>
    </aside>
  )
}

