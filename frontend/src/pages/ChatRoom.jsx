import { useState, useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { ChevronLeft, Send } from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"

export default function ChatRoom() {
  const navigate = useNavigate()
  const { id } = useParams()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const bottomRef = useRef(null)

  // 模拟聊天数据
  useEffect(() => {
    setMessages([
      { id: 1, content: "您好，请问这个车模还在吗？", isMine: true, time: "10:30" },
      { id: 2, content: "在的，随时可以拍", isMine: false, time: "10:32" },
      { id: 3, content: "价格能便宜点吗？", isMine: true, time: "10:33" },
      { id: 4, content: "最低1250包邮，可以吗？", isMine: false, time: "10:35" },
      { id: 5, content: "好的，价格可以商量", isMine: true, time: "10:36" },
    ])
  }, [id])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = () => {
    if (!input.trim()) return
    setMessages(prev => [...prev, {
      id: Date.now(),
      content: input,
      isMine: true,
      time: new Date().toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit" })
    }])
    setInput("")
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-lg z-40 px-4 pt-4 pb-3 border-b border-gray-100 flex items-center gap-3">
        <button onClick={() => navigate("/chat-list")} className="w-9 h-9 rounded-full flex items-center justify-center">
          <ChevronLeft size={22} className="text-secondary" />
        </button>
        <div className="flex-1">
          <p className="font-semibold text-secondary">车模老炮</p>
          <p className="text-xs text-text-secondary">AutoWorld 兰博基尼 Countach</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 pb-24">
        {messages.map((msg, i) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            className={`flex ${msg.isMine ? "justify-end" : "justify-start"}`}
          >
            <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 ${
              msg.isMine
                ? "bg-primary text-white rounded-br-md"
                : "bg-white text-secondary shadow-sm rounded-bl-md"
            }`}>
              <p className="text-sm leading-relaxed">{msg.content}</p>
              <p className={`text-xs mt-1 ${msg.isMine ? "text-white/60" : "text-text-secondary"}`}>{msg.time}</p>
            </div>
          </motion.div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-100 px-4 py-3 safe-bottom">
        <div className="flex items-center gap-3">
          <input
            type="text"
            placeholder="输入消息..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            className="flex-1 h-11 px-4 rounded-xl bg-gray-100 text-sm focus:outline-none"
          />
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={sendMessage}
            className="w-11 h-11 rounded-xl bg-primary flex items-center justify-center"
          >
            <Send size={18} className="text-white" />
          </motion.button>
        </div>
      </div>
    </div>
  )
}
