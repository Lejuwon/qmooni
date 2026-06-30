// src/components/ProjectList.jsx
import React from 'react';
import { useParams } from 'react-router-dom';
import { Plus, Pencil, Trash2 } from 'lucide-react';

export default function ProjectList({ projects, onAdd, onClick, onRename, onDelete }) {
  const { projectId } = useParams();            // URL에서 id 가져오기
  const currentId    = Number(projectId);       // 문자열 → 숫자

  return (
    <>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold">프로젝트</h2>
        <button onClick={onAdd} className="text-gray-700 hover:text-black">
          <Plus size={20} />
        </button>
      </div>
      <ul className="space-y-2">
        {projects.map((p) => {
          const isActive = p.topic_id === currentId;
          return (
            <li
              key={p.topic_id}
              onClick={() => onClick(p)}
              className={`
                flex items-center justify-between p-2 rounded cursor-pointer
                ${isActive 
                  ? 'bg-gray-200 font-semibold' 
                  : 'hover:bg-gray-100 text-gray-700'}
              `}
            >
              <div className="flex items-center space-x-2">
                <span>📁</span>
                <span>{p.title}</span>
              </div>
              <div className="flex items-center space-x-1">
                <button onClick={e => { e.stopPropagation(); onRename(p); }} className="p-1 hover:text-blue-500"><Pencil size={14}/></button>
                <button onClick={e => { e.stopPropagation(); onDelete(p); }} className="p-1 hover:text-red-500"><Trash2 size={14}/></button>
              </div>
            </li>
          );
        })}
      </ul>
    </>
  );
}