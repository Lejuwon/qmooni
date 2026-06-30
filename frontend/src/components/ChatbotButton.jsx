import chatbotIcon from '../assets/chatbotIcon.png'

export default function ChatbotButton({ projectId }) {
  return (
    <button
      onClick={() => window.location.href = `/project/${projectId}/chat`}
      className="flex items-center text-gray-700 hover:text-black mb-8"
    >
      <img src={chatbotIcon} alt="챗봇" className="w-6 h-6 mr-2" />
      챗봇
    </button>
  )
}
