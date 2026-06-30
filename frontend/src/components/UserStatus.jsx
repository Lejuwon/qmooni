import { useNavigate } from 'react-router-dom';
import { useAuth } from "../context/AuthContext";

export default function UserStatus() {
  const navigate = useNavigate();
  const { token, user, logout } = useAuth();

  // 로그인 안 된 상태
  if (!token) {
    return (
      <button
        onClick={() => navigate("/login")}
        className="bg-gray-100 px-3 py-1 rounded-full text-sm"
      >
        로그인
      </button>
    );
  }
  if (!user) {
    // 프로필 로딩 중일 때 혹은 에러 났을 때
    return <span>로딩…</span>;
  }

  // 로그인 된 상태
  return (
    <div className="flex items-center space-x-2">
      {user?.image_url && (
        <img
          src={user.image_url}
          alt={user.name}
          className="w-8 h-8 rounded-full"
        />
      )}
      {/* <span className="text-sm font-medium">{user.name || user.email}</span> */}
      <button
        onClick={logout}
        className="text-xs text-gray-500 hover:text-gray-700"
      >
        로그아웃
      </button>
    </div>
  );

  // const handleLogin = () => {
  //   navigate('/login'); // ✅ 로그인 페이지로 이동
  // };

  // return (
  //   <button onClick={handleLogin} className="bg-gray-100 px-3 py-1 rounded-full text-sm">
  //     로그인
  //   </button>
  // );
}
