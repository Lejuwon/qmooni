import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { callbackGoogle } from "../api/auth";
// import useAuth from "../hooks/useAuth";
import { useAuth } from "../context/AuthContext";

export default function AuthCallback() {
  const navigate = useNavigate();
  const { search } = useLocation();
  const { login } = useAuth();

  useEffect(() => {
    const token = new URLSearchParams(search).get("token");
    if (token) {
      login(token);
      navigate("/", { replace: true });
    } else {
      navigate("/login", { replace: true });
    }

    // const code = new URLSearchParams(search).get("code");
    // if (!code) return navigate("/login", { replace: true });

    // callbackGoogle(code)
    //     .then(data => {
    //         login(data.access_token);
    //         navigate("/", { replace: true });
    //     })
    //     .catch(() => navigate("/login", { replace: true }));
  }, [search, login, navigate]);

  return <div className="flex h-screen items-center justify-center">로그인 중…</div>;
}
