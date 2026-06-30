// ProjectFileUpload.jsx
import React, { forwardRef } from 'react';
import { useAuth }      from '../context/AuthContext';

const ProjectFileUpload = forwardRef(({ topicId, onUploadSuccess }, ref) => {
  const { token } = useAuth();
  const backend = process.env.REACT_APP_BACKEND_URL;

  const handleChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // ⚠️ FormData 로 감싼다
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(
        `${backend}/api/topics/${topicId}/documents`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            // Content-Type 는 브라우저가 자동으로 처리합니다.
          },
          body: formData,
        }
      );
      if (!res.ok) throw new Error(await res.text());
      const newDoc = await res.json();
      onUploadSuccess(newDoc);
    } catch (err) {
      console.error('파일 업로드 실패', err);
      alert('파일 업로드에 실패했습니다.');
    }
  };

  return (
    <input
      ref={ref}
      type="file"
      className="hidden"
      onChange={handleChange}
    />
  );
});

export default ProjectFileUpload;

// import { forwardRef } from 'react';
// import { useAuth }      from '../context/AuthContext';
// import { useParams }    from 'react-router-dom';

// const ProjectFileUpload = forwardRef((props, ref) => {
//   const { token } = useAuth();
//   const { projectId } = useParams();
//   const backend = process.env.REACT_APP_BACKEND_URL;

//   const handleChange = async (e) => {
//     const files = Array.from(e.target.files);
//     for (const file of files) {
//       const form = new FormData();
//       form.append('file', file);
//       form.append('topic_id', projectId);

//       const res = await fetch(`${backend}/api/topics/${projectId}/documents`, {
//         method: 'POST',
//         headers: {
//           // "Content-Type": "application/json",
//           'Authorization': `Bearer ${token}`,
//         },
//         body: form,
//       });

//       if (!res.ok) {
//         console.error('파일 업로드 실패', await res.text());
//       } else {
//         // 업로드 성공 후 목록 갱신 이벤트
//         window.dispatchEvent(new Event('documentUploaded'));
//       }
//     }
//     // 선택 후에도 input.value를 비워줘서, 같은 파일 다시 선택 가능하게
//     // e.target.value = '';
//     if (ref && ref.current) {
//       ref.current.value = null;
//     }
//   };

//   return (
//     <input
//       ref={ref}
//       type="file"
//       multiple={false}
//       className="hidden"
//       onChange={handleChange}
//     />
//   );
// });

// export default ProjectFileUpload;
