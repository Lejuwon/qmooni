// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";

console.log(process.env.REACT_APP_BACKEND_URL)

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("jwt"));
  const [user, setUser] = useState(null);

  // 토큰이 바뀌면 유저 프로필을 fetch
  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }

    // 환경변수로 불러온 백엔드 베이스 URL
    const backend = process.env.REACT_APP_BACKEND_URL;
    console.log("backend URL:", backend);

    fetch(`${backend}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) throw new Error("Not authenticated");
        return res.json();
      })
      .then((data) => setUser(data))
      .catch(() => {
        setToken(null);
        localStorage.removeItem("jwt");
        setUser(null);
      });
  }, [token]);

  const login = (jwt) => {
    localStorage.setItem("jwt", jwt);
    setToken(jwt);
    // user는 위 useEffect에서 자동으로 fetch돼서 setUser 됩니다.
  };

  const logout = () => {
    localStorage.removeItem("jwt");
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    const onStorage = (e) => {
      if (e.key === "jwt") setToken(e.newValue);
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// 👉 named export only
export function useAuth() {
  return useContext(AuthContext);
}
