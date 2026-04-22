import { motion } from "framer-motion"
import { Star, ChevronRight, Settings, ShoppingBag, Package, Heart, TrendingUp, MessageCircle } from "lucide-react"
import { useNavigate } from "react-router-dom"
import useStore from "../store/useStore"

const menuItems = [
  { icon: ShoppingBag, label: "我买到的", value: "3件" },
  { icon: Package, label: "我卖出的", value: "8件" },
  { icon: Heart, label: "我的喜欢", value: "23件" },
  { icon: TrendingUp, label: "价格行情", value: "", path: "/trend" },
  { icon: MessageCircle, label: "我的消息", value: "3", path: "/chat-list" },
]

export default function Profile({ user }) {
  const navigate = useNavigate()
  const { collections, getCollectionStats } = useStore()
  const stats = getCollectionStats()

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-lg z-40 px-4 pt-4 pb-3 flex items-center justify-between">
        <h1 className="text-xl font-bold text-secondary">我的</h1>
        <button className="w-9 h-9 rounded-full bg-white border border-gray-100 flex items-center justify-center">
          <Settings size={18} className="text-text-secondary" />
        </button>
      </div>

      {/* User Card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-4 mt-2 bg-gradient-to-r from-primary to-primary-dark rounded-2xl p-5 shadow-lg shadow-primary/20"
      >
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center text-3xl">
            🚗
          </div>
          <div className="flex-1">
            <h2 className="text-white text-xl font-bold">{user.name}</h2>
            <p className="text-white/70 text-sm mt-0.5">{user.phone}</p>
            <div className="flex items-center gap-1 mt-1">
              <Star size={14} className="text-accent fill-accent" />
              <span className="text-white text-sm font-medium">{user.rating}</span>
              <span className="text-white/60 text-sm ml-1">信用极好</span>
            </div>
          </div>
          <ChevronRight size={20} className="text-white/60" />
        </div>
      </motion.div>

      {/* Collection Summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="mx-4 mt-4 bg-white rounded-2xl p-4 shadow-sm"
      >
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm font-medium text-secondary">收藏概览</p>
          <button onClick={() => navigate("/collection")} className="text-sm text-primary">查看全部</button>
        </div>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <p className="text-xl font-bold text-secondary">{stats.total}</p>
            <p className="text-xs text-text-secondary">收藏数</p>
          </div>
          <div>
            <p className="text-xl font-bold text-secondary">¥{(stats.totalValue/1000).toFixed(1)}k</p>
            <p className="text-xs text-text-secondary">总估值</p>
          </div>
          <div>
            <p className={`text-xl font-bold ${stats.profit >= 0 ? "text-success" : "text-error"}`}>
              {stats.profit >= 0 ? "+" : ""}{Math.abs(stats.profit) >= 0 ? "+" : ""}{(stats.profit/1000).toFixed(1)}k
            </p>
            <p className="text-xs text-text-secondary">累计收益</p>
          </div>
        </div>
      </motion.div>

      {/* Menu */}
      <div className="mx-4 mt-4 bg-white rounded-2xl overflow-hidden shadow-sm">
        {menuItems.map(({ icon: Icon, label, value, path }, i) => (
          <motion.button
            key={label}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            onClick={() => path && navigate(path)}
            className="w-full flex items-center gap-4 px-4 py-4 border-b border-gray-50 last:border-0"
          >
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Icon size={18} className="text-primary" />
            </div>
            <span className="flex-1 text-left text-sm font-medium text-secondary">{label}</span>
            {value && <span className="text-sm text-primary font-medium">{value}</span>}
            <ChevronRight size={16} className="text-text-secondary" />
          </motion.button>
        ))}
      </div>

      {/* Settings */}
      <div className="mx-4 mt-4 bg-white rounded-2xl overflow-hidden shadow-sm">
        {[
          { label: "地址管理", emoji: "📍" },
          { label: "支付方式", emoji: "💳" },
          { label: "隐私设置", emoji: "🔒" },
          { label: "帮助中心", emoji: "❓" },
        ].map(({ label, emoji }, i) => (
          <motion.button
            key={label}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 + i * 0.04 }}
            className="w-full flex items-center gap-4 px-4 py-4 border-b border-gray-50 last:border-0"
          >
            <span className="text-xl">{emoji}</span>
            <span className="flex-1 text-left text-sm font-medium text-secondary">{label}</span>
            <ChevronRight size={16} className="text-text-secondary" />
          </motion.button>
        ))}
      </div>

      <p className="text-center text-xs text-text-secondary mt-8 pb-8">车模星球 v0.0.2</p>
    </div>
  )
}
