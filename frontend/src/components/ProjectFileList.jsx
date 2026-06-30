// ProjectFileList.jsx
import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'

export default function ProjectFileList({ topicId }) {
  const { token } = useAuth()
  const backend   = process.env.REACT_APP_BACKEND_URL
  const [docs, setDocs] = useState([])

  useEffect(() => {
    // 실제 목록을 불러오는 함수
    async function loadDocs() {
      try {
        const res = await fetch(
          `${backend}/api/topics/${topicId}/documents`,
          { headers: { Authorization: `Bearer ${token}` } }
        )
        if (res.ok) {
          setDocs(await res.json())
        }
      } catch (err) {
        console.error('문서 목록 로드 실패', err)
      }
    }

    // 1) 컴포넌트 마운트 시 한 번
    loadDocs()
    // 2) 업로드 성공 이벤트가 발생할 때마다 다시
    window.addEventListener('documentUploaded', loadDocs)
    // 3) 언마운트 시 정리
    return () => window.removeEventListener('documentUploaded', loadDocs)
  }, [backend, topicId, token])

  const handleDelete = async documentId => {
    if (!window.confirm('삭제하시겠습니까?')) return
    try {
      const res = await fetch(
        // topicId와 documentId를 함께 경로에 실어야 FastAPI 라우터가 잡습니다.
        `${backend}/api/topics/${topicId}/documents/${documentId}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      if (!res.ok) throw new Error(res.statusText)
      setDocs(prev => prev.filter(d => d.document_id !== documentId))
    } catch (err) {
      console.error('삭제 실패', err)
    }
  }

  if (!docs.length) {
    return <p className="text-gray-400 italic">업로드된 파일이 없습니다.</p>
  }
  return (
    <div className="space-y-2">
      {docs.map(d => (
        <div key={d.document_id} className="flex justify-between items-center bg-gray-50 p-3 rounded border">
          <div className="flex items-center space-x-2">
            <input type="checkbox" />
            <span>{d.file_name}</span>
          </div>
          <div className="flex space-x-2">
            <a
              href={`${backend}/${d.file_url}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 text-sm hover:underline"
            >미리보기</a>
            <button
              onClick={() => handleDelete(d.document_id)}
              className="text-red-500 text-sm hover:underline"
            >삭제</button>
          </div>
        </div>
      ))}
    </div>
  )
}