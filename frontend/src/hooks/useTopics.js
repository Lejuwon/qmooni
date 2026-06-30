import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

export function useTopics() {
  const { token } = useAuth();
  const backend = process.env.REACT_APP_BACKEND_URL;
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);

  // 1) 전체 불러오기
  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await fetch(`${backend}/api/topics`, {
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });
      if (!res.ok) throw new Error('Failed to fetch');
      setTopics(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [backend, token]);

  // 2) 생성
  const create = useCallback(async (initialTitle) => {
    if (!initialTitle) return;
    let title = initialTitle;
    // 반복해서 중복 체크
    while (topics.some(t => t.title === title)) {
      title = window.prompt('이미 같은 이름의 프로젝트가 있습니다. 다른 이름을 입력해주세요:', title);
      if (title === null || title.trim() === '') return; // 취소 또는 빈 문자열 시 중단
    }
    const res = await fetch(`${backend}/api/topics`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error('Failed to create topic');
    const newTopic = await res.json();
    setTopics((t) => [...t, newTopic]);
  }, [backend, token, topics]);

  // const create = useCallback(async (title) => {
  //   const res = await fetch(`${backend}/api/topics`, {
  //     method: 'POST',
  //     headers: {
  //       'Content-Type': 'application/json',
  //       'Authorization': `Bearer ${token}`,
  //     },
  //     body: JSON.stringify({ title }),
  //   });
  //   if (!res.ok) throw new Error('Failed to create');
  //   const newTopic = await res.json();
  //   setTopics((t) => [...t, newTopic]);
  // }, [backend, token]);

  // 3) 수정
  const update = useCallback(async (id, initialTitle) => {
    if (!initialTitle) return;
    let title = initialTitle;
    // 중복 체크, 자기 자신 제외
    while (topics.some(t => t.title === title && t.topic_id !== id)) {
      title = window.prompt('이미 같은 이름의 프로젝트가 있습니다. 다른 이름을 입력해주세요:', title);
      if (title === null || title.trim() === '') return;
    }
    const res = await fetch(`${backend}/api/topics/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error('Failed to update topic');
    const updated = await res.json();
    setTopics((t) => t.map((x) => x.topic_id === id ? updated : x));
  }, [backend, token, topics]);
  // const update = useCallback(async (id, title) => {
  //   const res = await fetch(`${backend}/api/topics/${id}`, {
  //     method: 'PUT',
  //     headers: {
  //       'Content-Type': 'application/json',
  //       'Authorization': `Bearer ${token}`,
  //     },
  //     body: JSON.stringify({ title }),
  //   });
  //   if (!res.ok) throw new Error('Failed to update');
  //   const updated = await res.json();
  //   setTopics((t) => t.map((x) => x.topic_id === id ? updated : x));
  // }, [backend, token]);

  // 4) 삭제
  const remove = useCallback(async (id) => {
    const res = await fetch(`${backend}/api/topics/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    if (!res.ok) throw new Error('Failed to delete');
    setTopics((t) => t.filter((x) => x.topic_id !== id));
  }, [backend, token]);

  // 마운트 시 자동 로드
  useEffect(() => { load(); }, [load]);

  return { topics, loading, load, create, update, remove };
}
