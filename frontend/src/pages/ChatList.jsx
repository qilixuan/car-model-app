import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { MessageCircle, ChevronRight } from "lucide-react"
import { useNavigate } from "react-router-dom"

export default function ChatList() {
  const navigate = useNavigate()
  const [rooms, setRooms] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 模拟聊天列表数据
    setTimeout(() => {
      setRooms([
        { id: 1, productName: "AutoWorld 兰博基尼 Countach", otherUser: "车模老炮", lastMsg: "好的，价格可以商量", time: "刚刚" },
        { id: 2, productName: "ISO  保时捷 911 GT3 RS", otherUser: "速度机器", lastMsg: "您好，请问什么时候发货", time: "10分钟前" },
        { id: 3, productName: "Tommy教父 法拉利 F40", otherUser: "跃马收藏", lastMsg: "收到，感谢购买！", time: "昨天" },
      ])
      setLoading(false)
    }, 500)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      <div className="sticky top-0 bg-background/95 backdrop-blur-lg z-40 px-4 pt-4 pb-3 border-b border-gray-100">
        <h1 className="text-xl font-bold text-secondary">我的消息</h1>
      </div>

      {loading ? (
        <div className="p-4 space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-white rounded-2xl p-4 skeleton h-20" />
          ))}
        </div>
      ) : rooms.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20">
          <MessageCircle size={48} className="text-text-secondary mb-3" />
          <p className="text-text-secondary">暂无消息</p>
          <p className="text-text-secondary text-sm mt-1">去市场看看心仪的车模吧</p>
          <button onClick={() => navigate("/market")} className="mt-4 px-6 py-2 rounded-xl bg-primary text-white text-sm font-medium">
            去市场
          </button>
        </div>
      ) : (
        <div className="p-4 space-y-3">
          {rooms.map((room, i) => (
            <motion.div
              key={room.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => navigate(`/chat/${room.id}`)}
              className="bg-white rounded-2xl p-4 shadow-sm cursor-pointer active:bg-gray-50"
            >
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-2xl flex-shrink-0">
                  🚗
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="font-medium text-secondary text-sm truncate">{room.otherUser}</p>
                    <span className="text-xs text-text-secondary">{room.time}</span>
                  </div>
                  <p className="text-xs text-text-secondary mt-0.5 truncate">{room.productName}</p>
                  <p className="text-sm text-text-secondary mt-1 truncate">{room.lastMsg}</p>
                </div>
                <ChevronRight size={16} className="text-text-secondary flex-shrink-0" />
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
