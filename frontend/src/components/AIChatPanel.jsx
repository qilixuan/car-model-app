import { useState, useRef, useEffect } from 'react'
import { X, Send, Sparkles, User } from 'lucide-react'

const aiReplies = {
  greeting: "宝～我是星仔呀！车模星球的小助手，有任何关于车模的问题尽管问我哒！",
  search: "好的宝～我帮你找找这款车模的信息！稍等一下哦～",
  collection: "收到！让我来帮你整理一下收藏～",
  price: "关于价格嘛，我帮你查一下近期市场价哦！",
  unknown: "宝～这个问题我正在学习中，让我结合你的情况给你一个合适的建议呀～"
}

function getReply(message) {
  const m = message.toLowerCase()
  if (m.includes('查') || m.includes('找') || m.includes('看')) return aiReplies.search
  if (m.includes('收藏') || m.includes('整理') || m.includes('添加')) return aiReplies.collection
  if (m.includes('价') || m.includes('钱') || m.includes('值')) return aiReplies.price
  if (m.includes('你好') || m.includes('嗨') || m.includes('在')) return aiReplies.greeting
  return aiReplies.unknown
}

export default function AIChatPanel({ open, onClose }) {
  if (!open) return null

  const [messages, setMessages] = useState([
    { role: 'assistant', content: aiReplies.greeting }
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return
    const userMsg = { role: 'user', content: input.trim() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsTyping(true)
    await new Promise(r => setTimeout(r, 800 + Math.random() * 600))
    const reply = { role: 'assistant', content: getReply(input) }
    setMessages(prev => [...prev, reply])
    setIsTyping(false)
  }

  return (
    <div className="fixed inset-0 z-[100] flex flex-col bg-white">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gradient-to-r from-primary to-primary-dark">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
            <Sparkles size={18} className="text-white" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm">星仔 AI 助手</div>
            <div className="text-white/70 text-xs">车模星球专属 · 在线</div>
          </div>
        </div>
        <button onClick={onClose} className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
          <X size={18} className="text-white" />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Sparkles size={14} className="text-primary" />
              </div>
            )}
            <div className={`max-w-[75%] rounded-2xl px-3 py-2 text-sm ${msg.role === 'user' ? 'bg-primary text-white rounded-tr-sm' : 'bg-gray-100 text-text-primary rounded-tl-sm'}`}>
              {msg.content}
            </div>
            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                <User size={14} className="text-primary" />
              </div>
            )}
          </div>
        ))}
        {isTyping && (
          <div className="flex gap-2">
            <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center">
              <Sparkles size={14} className="text-primary" />
            </div>
            <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-3 py-2">
              <div className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="p-3 border-t border-gray-100 bg-white">
        <div className="flex gap-2 items-end">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="问星仔任何车模问题..."
            className="flex-1 h-10 px-4 rounded-full bg-gray-100 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="w-10 h-10 rounded-full bg-primary flex items-center justify-center disabled:opacity-40 active:scale-95 transition-transform"
          >
            <Send size={16} className="text-white" />
          </button>
        </div>
        <div className="text-center text-xs text-gray-400 mt-2">
          AI 助手由 星仔 提供支持 · 车模星球
        </div>
      </div>
    </div>
  )
}
