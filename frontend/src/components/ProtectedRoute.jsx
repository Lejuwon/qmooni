// import { useState, useEffect } from "react";
// export default function useAuth() {
//   const [token, setToken] = useState(localStorage.getItem("jwt"));
//   const login = (jwt) => {
//     localStorage.setItem("jwt", jwt);
//     setToken(jwt);
//   };
//   const logout = () => {
//     localStorage.removeItem("jwt");
//     setToken(null);
//   };
//   return { token, login, logout };
// }

// import { Navigate } from "react-router-dom";

// export default function ProtectedRoute({ token, children }) {
//   // 토큰이 없으면 로그인 화면으로
//   if (!token) {
//     return <Navigate to="/login" replace />;
//   }
//   // 토큰이 있으면 자식 컴포넌트를 렌더
//   return <>{children}</>;
// }
