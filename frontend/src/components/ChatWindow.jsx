// src/components/ChatWindow.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';

export default function ChatWindow({ topicId, sessionId, onNewSession }) {
  const { token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput]       = useState('');
  const scrollRef = useRef();

  // ① 이전 메시지 불러오기
  useEffect(() => {
    if (!sessionId) return;
    fetch(`${process.env.REACT_APP_BACKEND_URL}/api/chat/sessions/${sessionId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(res => res.ok ? res.json() : Promise.reject(res.status))
      .then(data => setMessages(data))
      .catch(console.error);
  }, [sessionId, token]);

  // ② 스크롤 바닥 유지
  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages]);

  // ③ 메시지 전송
  const sendMessage = async () => {
    const text = input.trim();
    if (!text) return;
    setInput('');

    // 신규 세션이면 /api/chat/{topicId}, 아니면 /api/chat/sessions/{sessionId}
    const path = sessionId
      ? `/api/chat/sessions/${sessionId}`
      : `/api/chat/${topicId}`;

    const res = await fetch(
      `${process.env.REACT_APP_BACKEND_URL}${path}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: text }),
      }
    );

    if (!res.ok) {
      console.error('메시지 전송 실패', await res.text());
      return;
    }
    const data = await res.json();

    // 신규 세션이라면 callback
    if (!sessionId && data.session_id) {
      onNewSession(data.session_id);
    }

    // 화면에 바로 반영
    setMessages(prev => [
      ...prev,
      { sender_type: 'user', message: text },
      { sender_type: 'bot',  message: data.answer },
    ]);
  };

  return (
    <div className="flex flex-col h-full">
      {/* 메시지 리스트 */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-auto p-4 flex flex-col items-center space-y-4"
      >
        {messages.map((m, i) => (
          <div
            key={i}
            className={`
              max-w-[70%] px-4 py-2
              ${m.sender_type === 'bot'
                ? 'self-start'
                : 'bg-gray-100 self-end'}
            rounded-2xl text-left`}
          >
            {m.message}
          </div>
        ))}
      </div>

      {/* 입력창 */}
      <div className="mt-auto sticky bottom-0 p-4 border-t flex bg-white">
        <input
          className="flex-1 border rounded-full px-4 py-2 focus:outline-none"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="큐무니에게 무엇이든 물어보세요"
        />
        <button
          onClick={sendMessage}
          className="w-10 h-10 flex items-center justify-center bg-gray-500 rounded-full hover:bg-gray-600"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            preserveAspectRatio="xMidYMid meet"
            className="w-5 h-5 text-white"
          >
            {/* 8,5 에서 16,12 로 올라갔다가 8,19 로 내려오는 화살표 */}
            <path 
              fill="currentColor"
              d="M8 5 L16 12 L8 19 Z"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}

// // src/components/ChatWindow.jsx
// import React, { useState, useEffect } from 'react'
// import { useAuth } from '../context/AuthContext'

// export default function ChatWindow({ topicId, sessionId, onNewSession }) {
//   const { token } = useAuth()
//   const [messages, setMessages] = useState([])
//   const [input, setInput]     = useState('')

//   // ① 기존 대화 불러오기
//   useEffect(() => {
//     if (!sessionId) return
//     fetch(`${process.env.REACT_APP_BACKEND_URL}/api/chat/sessions/${sessionId}`, {
//       headers: { Authorization: `Bearer ${token}` },
//     })
//       .then(res => res.ok ? res.json() : Promise.reject(res.status))
//       .then(data => setMessages(data))
//       .catch(console.error)
//   }, [sessionId, token])

//   // ② 메시지 전송 로직
//   const sendMessage = async () => {
//     const text = input.trim()
//     if (!text) return

//     // POST 경로: 새 세션이냐 이어쓰기냐에 따라 달라져요
//     const url = sessionId
//       ? `/api/chat/sessions/${sessionId}`
//       : `/api/chat/${topicId}`

//     const res = await fetch(
//       `${process.env.REACT_APP_BACKEND_URL}${url}`,
//       {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           Authorization: `Bearer ${token}`,
//         },
//         body: JSON.stringify({ message: text }),
//       }
//     )

//     if (!res.ok) {
//       console.error('메시지 전송 실패', await res.text())
//       return
//     }
//     const data = await res.json()

//     // 신규 세션이 만들어졌다면 부모에 알려 줍니다
//     if (!sessionId && data.session_id) {
//       onNewSession(data.session_id)
//     }

//     // 사용자 메시지 + 봇 응답
//     setMessages(prev => [
//       ...prev,
//       { sender_type: 'user', message: text },
//       { sender_type: 'bot',  message: data.answer },
//     ])
//     setInput('')
//   }

//   return (
//     <div className="flex flex-col h-full">
//       {/* 메시지 목록 */}
//       <div className="flex-1 overflow-auto p-4 space-y-2">
//         {messages.map((m, i) => (
//           <div
//             key={i}
//             className={`max-w-[70%] p-2 rounded ${
//               m.sender_type === 'bot'
//                 ? 'bg-gray-100 self-start'
//                 : 'bg-blue-100 self-end'
//             }`}
//           >
//             {m.message}
//           </div>
//         ))}
//       </div>

//       {/* 입력창 */}
//       <div className="p-4 border-t flex">
//         <input
//           className="flex-1 border rounded-l px-2 py-1 focus:outline-none"
//           value={input}
//           onChange={e => setInput(e.target.value)}
//           onKeyDown={e => e.key === 'Enter' && sendMessage()}
//           placeholder="큐무니에게 무엇이든 물어보세요"
//         />
//         <button
//           className="bg-blue-500 text-white px-4 rounded-r hover:bg-blue-600"
//           onClick={sendMessage}
//         >
//           ▶
//         </button>
//       </div>
//     </div>
//   )
// }
