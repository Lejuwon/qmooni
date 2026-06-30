export async function callbackGoogle(code) {
  const res = await fetch(
    `${process.env.REACT_APP_API_URL}/auth/google/callback?code=${code}`
  );
  if (!res.ok) throw new Error("구글 로그인 콜백 실패");
  return res.json();
}

export async function fetchMe(token) {
  const res = await fetch(`${process.env.REACT_APP_API_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("사용자 정보 가져오기 실패");
  return res.json();
}