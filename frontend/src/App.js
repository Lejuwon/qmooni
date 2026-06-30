import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import AuthCallback from "./pages/AuthCallback";
import HomePage from "./pages/HomePage";
import ProjectPage from "./pages/ProjectPage";
import ChatPage     from './pages/ChatPage';
import QuizPage     from "./pages/QuizPage";
import QuizWindow from './components/QuizWindow'
import QuizResultPage from './pages/QuizResultPage'

export default function App() {
  const { token } = useAuth();

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/" element={<HomePage />} />
        <Route path="/project/:projectId" element={<ProjectPage />} />
        <Route path="/project/:projectId/chat" element={<ChatPage />} />
        <Route path="/project/:projectId/chat/:sessionId?" element={<ChatPage />} />
        <Route path="/project/:projectId/quiz/:attemptId/result" element={<QuizResultPage />} />
        <Route path="/project/:projectId/quiz/:attemptId" element={<QuizWindow />} />
        <Route path="/project/:projectId/quiz" element={<QuizPage />} />
      </Routes>
    </BrowserRouter>
  );
}
