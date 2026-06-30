export default function LoginPage() {
  const handleGoogleLogin = () => {
    const base = "https://accounts.google.com/o/oauth2/v2/auth";
    const params = new URLSearchParams({
      client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
      redirect_uri: process.env.REACT_APP_GOOGLE_REDIRECT_URI,
      response_type: "code",
      scope: "email profile"
    });
    window.location.href = `${base}?${params}`;
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <button
        onClick={handleGoogleLogin}
        className="bg-blue-500 text-white px-6 py-2 rounded"
      >
        구글로 로그인
      </button>
    </div>
  );
}
