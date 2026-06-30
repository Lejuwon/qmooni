// src/components/Header.jsx
import { Link, useParams } from 'react-router-dom';
import { useTopics } from '../hooks/useTopics';
import UserStatus from './UserStatus';

export default function Header() {
  const { projectId } = useParams();
  const { topics } = useTopics();
  const current = topics.find(t => t.topic_id === Number(projectId));

  return (
    <header className="flex items-center justify-between p-4 border-b border-gray-200">
      <div className="text-2xl font-bold flex items-center space-x-2">
        {/* 홈으로 돌아가는 링크 */}
        <Link to="/" className="hover:text-blue-600 transition-colors">Qmooni</Link>
        {current && (
          <>
            <span className="text-gray-500">›</span>
            <Link
              to={`/project/${projectId}`}
              className="hover:text-blue-600 transition-colors"
            >
              {current.title}
            </Link>
          </>
        )}
      </div>
      <UserStatus />
    </header>
  );
}

// import { useNavigate } from 'react-router-dom';
// import UserStatus from './UserStatus';

// export default function Header() {
//   const navigate = useNavigate();

//   return (
//     <header className="flex items-center justify-between p-4 border-b border-gray-200">
//       <h1
//         className="text-2xl font-bold cursor-pointer hover:text-blue-600 transition-colors"
//         onClick={() => navigate('/')}
//       >
//         Qmooni
//       </h1>
//       <UserStatus />
//     </header>
//   );
// }