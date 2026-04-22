import { useState } from "react"
import { Heart, Share2, MessageCircle, ChevronLeft, Star } from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"
import { motion } from "framer-motion"
import { mockProducts } from "../data/mockData"
import useStore from "../store/useStore"

export default function ProductDetail({ user }) {
  const navigate = useNavigate()
  const { id } = useParams()
  const { likedProducts, toggleLike } = useStore()
  const [currentImage, setCurrentImage] = useState(0)
  const [activeTab, setActiveTab] = useState("detail")

  const product = mockProducts.find(p => p.id === Number(id))
  if (!product) return <div className="p-4 text-center text-text-secondary">商品不存在</div>

  const isLiked = likedProducts.includes(product.id)

  const handleChat = () => {
    // 模拟进入聊天
    navigate(`/chat/${product.id}`)
  }

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="sticky top-0 z-50 flex items-center justify-between px-4 pt-4 pb-2 bg-background/80 backdrop-blur-lg">
        <button
          onClick={() => navigate(-1)}
          className="w-9 h-9 rounded-full bg-white/80 backdrop-blur flex items-center justify-center shadow-sm"
        >
          <ChevronLeft size={20} className="text-secondary" />
        </button>
        <div className="flex gap-2">
          <button className="w-9 h-9 rounded-full bg-white/80 backdrop-blur flex items-center justify-center shadow-sm">
            <Share2 size={16} className="text-secondary" />
          </button>
          <button
            onClick={() => toggleLike(product.id)}
            className="w-9 h-9 rounded-full bg-white/80 backdrop-blur flex items-center justify-center shadow-sm"
          >
            <Heart size={16} className={isLiked ? "fill-primary text-primary" : "text-secondary"} />
          </button>
        </div>
      </div>

      {/* Image Gallery */}
      <div className="px-4">
        <div className="relative aspect-square rounded-2xl overflow-hidden bg-gray-100">
          <img
            src={product.images[currentImage]}
            alt={product.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
            {product.images.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrentImage(i)}
                className={`w-1.5 h-1.5 rounded-full transition-colors ${i === currentImage ? "bg-white" : "bg-white/40"}`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Price & Info */}
      <div className="px-4 mt-4">
        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-primary text-2xl font-bold">¥{product.price.toLocaleString()}</p>
              {product.originalPrice > product.price && (
                <p className="text-text-secondary text-sm line-through mt-0.5">
                  原价 ¥{product.originalPrice.toLocaleString()}
                </p>
              )}
            </div>
            <div className="flex items-center gap-1 text-text-secondary text-sm">
              <Star size={14} className="text-accent fill-accent" />
              <span className="font-medium">{product.seller.rating}</span>
              <span className="text-xs">({product.seller.name})</span>
            </div>
          </div>

          <h1 className="text-lg font-bold text-secondary mt-3">{product.name}</h1>
          <p className="text-sm text-text-secondary mt-1">{product.brand} · {product.series}</p>

          <div className="flex gap-2 mt-3">
            {[
              { label: product.scale, bg: "bg-primary/10", text: "text-primary" },
              { label: product.condition, bg: "bg-success/10", text: "text-success" },
              { label: product.material, bg: "bg-accent/20", text: "text-warning" },
            ].map(({ label, bg, text }) => (
              <span key={label} className={`px-2.5 py-1 rounded-lg text-xs font-medium ${bg} ${text}`}>
                {label}
              </span>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="flex gap-3 mt-3">
          <div className="flex-1 bg-white rounded-xl p-3 shadow-sm text-center">
            <p className="text-lg font-bold text-secondary">{product.likes}</p>
            <p className="text-xs text-text-secondary">喜欢</p>
          </div>
          <div className="flex-1 bg-white rounded-xl p-3 shadow-sm text-center">
            <p className="text-lg font-bold text-secondary">{product.views}</p>
            <p className="text-xs text-text-secondary">浏览</p>
          </div>
          <div className="flex-1 bg-white rounded-xl p-3 shadow-sm text-center">
            <p className="text-lg font-bold text-secondary">{product.postedAt}</p>
            <p className="text-xs text-text-secondary">发布时间</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mt-4 border-b border-gray-100">
          {["detail", "seller"].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium transition-colors ${
                activeTab === tab ? "text-primary border-b-2 border-primary" : "text-text-secondary"
              }`}
            >
              {tab === "detail" ? "商品详情" : "卖家信息"}
            </button>
          ))}
        </div>

        {activeTab === "detail" ? (
          <div className="bg-white rounded-2xl p-4 shadow-sm mt-3">
            <p className="text-sm text-text-secondary leading-relaxed">{product.description}</p>
          </div>
        ) : (
          <div className="bg-white rounded-2xl p-4 shadow-sm mt-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-2xl">🚗</div>
              <div>
                <p className="font-medium text-secondary">{product.seller.name}</p>
                <div className="flex items-center gap-1 mt-0.5">
                  <Star size={12} className="text-accent fill-accent" />
                  <span className="text-sm text-text-secondary">信用 {product.seller.rating}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Action Bar */}
      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-white border-t border-gray-100 px-4 py-3 safe-bottom">
        <div className="flex gap-3">
          <button
            onClick={() => toggleLike(product.id)}
            className="flex items-center justify-center gap-2 h-12 px-5 rounded-xl border border-gray-200 text-secondary font-medium"
          >
            <Heart size={18} className={isLiked ? "fill-primary text-primary" : ""} />
            <span>收藏</span>
          </button>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleChat}
            className="flex items-center justify-center gap-2 h-12 px-5 rounded-xl border border-primary text-primary font-medium"
          >
            <MessageCircle size={18} />
            <span>聊一聊</span>
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.98 }}
            className="flex-1 h-12 rounded-xl bg-gradient-to-r from-primary to-primary-dark text-white font-semibold shadow-lg shadow-primary/30"
          >
            我想要
          </motion.button>
        </div>
      </div>
    </div>
  )
}
