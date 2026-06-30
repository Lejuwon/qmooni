// src/components/QmooniLayout.jsx
import React, { useState } from 'react';
import Chat from './ChatWindow';
import Sidebar from './Sidebar';
import Header from './Header';
import qmooniImage from '../assets/qmooni.png';
import { useAuth } from '../context/AuthContext';

export default function QmooniLayout({ children }) {
  const { token } = useAuth();
  const noContent = !children && !token;
  // const noContent = !children 
  // const [chatOpen, setChatOpen] = useState(false);

  return (
    <div className="flex h-screen">
      {/* 로그인 돼 있으면 사이드바 */}
      {token && <Sidebar />}
      {/* {token && <Sidebar onChatOpen={() => setChatOpen(true)} />} */}

      <div className="flex-1 flex flex-col">
        <Header />

        {/* 
          - noContent === true 이면 화면 전체를 flex 컨테이너로 만들어 
            가운데 정렬(flex items-center justify-center) 적용 
        */}
        <main
          // className={
          //   `flex-1 overflow-auto px-6 pt-48 text-center ` +
          //   (noContent ? 'flex items-center justify-center' : '')
          // }
          className={
            noContent
              ? 'flex-1 flex flex-col items-center justify-center text-center h-full'
              : 'flex-1 overflow-auto px-6 text-center'
          }
        >
          {children
            ? (
                /* children 이 있으면 그대로 렌더 */
                children
              )
            : (
                /* children 없고, 토큰도 없으면 hero graphic */
                <>
                  <img
                    src={qmooniImage}
                    alt="큐무니"
                    className="w-32 h-32 mb-6"
                  />
                  <p className="text-xl font-semibold text-gray-700 leading-relaxed">
                    “문서를 톡! 퀴즈로 쏙! <br />
                    큐무니와 함께 공부해요!”
                  </p>
                </>
              )
          }
        </main>
      </div>
    </div>
  );
}
