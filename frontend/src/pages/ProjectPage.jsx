// // ProjectPage.jsx
// import { useRef } from 'react'
// import { useParams } from 'react-router-dom'
// import { useAuth }   from '../context/AuthContext'
// import QmooniLayout  from '../components/QmooniLayout'
// import ProjectFileUpload  from '../components/ProjectFileUpload'
// import ProjectFileList    from '../components/ProjectFileList'

// export default function ProjectPage() {
//   const { token } = useAuth()
//   const { projectId } = useParams()
//   const uploadRef = useRef()

//   if (!token) return <QmooniLayout />

//   return (
//     <QmooniLayout>
//       <div className="space-y-6 px-4 mt-4">
//         <div className="justify-center items-start">
//           <button
//             className="border rounded-lg p-6 text-center cursor-pointer hover:bg-gray-100 h-48 items-center justify-center"
//             onClick={() => uploadRef.current?.click()}
//           >
//             <p className="text-xl font-bold mb-2">📁 파일 업로드</p>
//             <p className="text-sm text-gray-500">
//               이 프로젝트의 채팅이 파일 콘텐츠에 액세스할 수 있습니다
//             </p>
//           </button>
//         </div>
//       </div>

//       <ProjectFileUpload
//         ref={uploadRef}
//         topicId={projectId}
//         // 업로드 성공 시, 파일 리스트를 새로 불러오라고 ProjectFileList 에 알려주는 이벤트
//         onUploadSuccess={() => {
//           window.dispatchEvent(new Event('documentUploaded'))
//         }}
//       />

//       <div className="mt-6 space-y-6 px-4">
//         <ProjectFileList topicId={projectId} />
//       </div>
//     </QmooniLayout>
//   )
// }

import { useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
// import { useTopics } from '../hooks/useTopics';
import { useAuth }       from '../context/AuthContext';
import QmooniLayout from '../components/QmooniLayout';
import ProjectFileUpload from '../components/ProjectFileUpload';
import ProjectFileList from '../components/ProjectFileList';

export default function ProjectPage() {
  const { token } = useAuth();
  const { projectId } = useParams();
  const uploadRef = useRef(); // ✅ input 제어용 ref
  const [docs, setDocs] = useState([])
  
  // 세션(토큰) 없으면 헬퍼 페이지(로고+문구)만 띄우고 사이드바도 숨김
  if (!token) {
    return <QmooniLayout />;
  }

  const handleUploadClick = () => {
    uploadRef.current?.click(); // ✅ 업로드 클릭 시 input 트리거
  };

  const handleUploadSuccess = newDoc => {
    setDocs(prev => [newDoc, ...prev])
  }

  return (
    <QmooniLayout>
      <div className="space-y-6 px-4 mt-4">
        <div className="justify-center items-start">
          <div
            className="border rounded-lg p-6 text-center cursor-pointer hover:bg-gray-100 h-40 items-center flex flex-col justify-center"
            onClick={handleUploadClick}
          >
            <p className="text-xl font-bold mb-2">📁 파일 업로드</p>
            <p className="text-sm text-gray-500">
              이 프로젝트의 채팅이 파일 콘텐츠에 액세스할 수 있습니다
            </p>
          </div>
        </div>
      </div>

      <ProjectFileUpload
        ref={uploadRef}
        topicId={projectId}
        // 업로드 성공 시, 파일 리스트를 새로 불러오라고 ProjectFileList 에 알려주는 이벤트
        onUploadSuccess={() => {
          window.dispatchEvent(new Event('documentUploaded'))
        }}
      />

      <div className="mt-6 space-y-6 px-4">
        <ProjectFileList topicId={projectId} />
      </div>
      {/* 숨겨진 input (업로드 로직 포함) */}
      {/* <ProjectFileUpload
        ref={uploadRef}
        topicId={projectId}
        onUploadSuccess={handleUploadSuccess}
      /> */}

      {/* 문서 리스트: docs state를 넘겨서 렌더링 */}
      {/* <div className="mt-6 space-y-6 px-4">
        <ProjectFileList
          topicId={projectId}
          docs={docs}
          onRemove={docId =>
            setDocs(prev => prev.filter(d => d.document_id !== docId))
          }
        />
      </div> */}
    </QmooniLayout>
  );
}
