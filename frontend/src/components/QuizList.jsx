// src/components/QuizList.jsx
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuizApi } from '../hooks/useQuizApi';

export default function QuizList() {
  const { projectId, attemptId: activeId } = useParams();
  const navigate = useNavigate();
  const { fetchAttempts } = useQuizApi();
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAttempts()
      .then(setList)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>로딩 중…</p>;
  if (!list.length) return <p className="text-gray-400 italic">퀴즈 이력이 없습니다.</p>;

  return (
    <ul className="space-y-2 overflow-auto max-h-[calc(100vh-10rem)]">
      {list.map(a => {
        const isActive = String(a.attemptId) === activeId;
        return (
          <li key={a.attemptId}>
            <button
              onClick={() => navigate(`/project/${projectId}/quiz/${a.attemptId}/result`)}
              className={`w-full text-left px-4 py-2 rounded-lg transition 
                ${isActive ? 'bg-gray-200 font-medium' : 'hover:bg-gray-100'}`}
            >
              {a.attemptTitle}
              {/* <div className="text-xs text-gray-500">{new Date(a.createdAt).toLocaleString()}</div> */}
            </button>
          </li>
        );
      })}
    </ul>
  );
}

// import React from 'react'

// export default function QuizList({ docs = [], selectedDocId, onSelect }) {
//   if (!docs.length) {
//     return <p className="text-gray-400 italic">문서가 없습니다.</p>
//   }

//   return (
//     <ul className="space-y-2">
//       {docs.map(doc => {
//         const isActive = doc.document_id === selectedDocId
//         return (
//           <li
//             key={doc.document_id}
//             onClick={() => onSelect(doc)}
//             className={`cursor-pointer p-2 rounded-lg transition-colors
//               ${isActive
//                 ? 'bg-gray-200 font-medium'
//                 : 'bg-transparent hover:bg-gray-100'}
//             `}
//           >
//             {doc.file_name}
//           </li>
//         )
//       })}
//     </ul>
//   )
// }