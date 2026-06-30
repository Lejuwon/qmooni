// src/pages/HomePage.jsx
import React from "react";
import { useAuth } from "../context/AuthContext";
import QmooniLayout from "../components/QmooniLayout";
import hpqmooniImage from '../assets/homePageQmooni.png';

export default function HomePage() {
  const { token } = useAuth();

  // ── 로그인 전: children 없이 레이아웃만 넘겨 줘서 큐문이+인삿말만 보이게
  if (!token) {
    return <QmooniLayout />;
  }

  // ── 로그인 후: layout 안에 실제 메인 콘텐츠 렌더
  return (
    <QmooniLayout>
      <div className="flex-1 flex flex-col items-center justify-center text-center h-full">
        <img
          src={hpqmooniImage}
          alt="큐무니"
          className="w-32 h-32 mb-6"
        />
        <p className="text-xl font-semibold text-gray-700 leading-relaxed">
          환영합니다! <br />
          주제를 생성해주세요!
        </p>
        {/* 기존에 HomePage에서 보여주던 컴포넌트들 */}
      </div>
    </QmooniLayout>
  );
}
