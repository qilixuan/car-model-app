import { Heart, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import useStore from '../store/useStore'

// 稀缺度配置
const rarityConfig = {
  '普款': { label: '普款', color: 'bg-gray-100 text-gray-500' },
  '稀有': { label: '稀有', color: 'bg-blue-100 text-blue-600' },
  '超稀有': { label: '超稀有', color: 'bg-purple-100 text-purple-600' },
  '神物': { label: '神物', color: 'bg-amber-100 text-amber-600' },
}

// 价格趋势配置
const trendConfig = {
  '上涨': { icon: TrendingUp, color: 'text-red-500' },
  '稳定': { icon: Minus, color: 'text-gray-400' },
  '下跌': { icon: TrendingDown, color: 'text-green-500' },
}

export default function ProductCard({ product }) {
  const navigate = useNavigate()
  const { likedProducts, toggleLike } = useStore()
  const isLiked = likedProducts.includes(product.id)

  const rarity = rarityConfig[product.rarity] || { label: product.rarity || '普款', color: 'bg-gray-100 text-gray-500' }
  const trend = trendConfig[product.priceTrend] || { icon: Minus, color: 'text-gray-400' }
  const TrendIcon = trend.icon

  // 市场价格范围
  const hasMarketPrice = product.marketPriceLow && product.marketPriceHigh

  return (
    <motion.div
      whileTap={{ scale: 0.97 }}
      onClick={() => navigate(`/product/${product.id}`)}
      className="bg-surface rounded-2xl overflow-hidden shadow-sm cursor-pointer"
    >
      <div className="relative aspect-square bg-gray-100">
        {product.images?.[0] ? (
          <img
            src={product.images[0]}
            alt={product.name}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300 text-4xl">
            🚗
          </div>
        )}
        <button
          onClick={(e) => { e.stopPropagation(); toggleLike(product.id) }}
          className="absolute top-2 right-2 w-8 h-8 rounded-full bg-white/80 backdrop-blur flex items-center justify-center"
        >
          <Heart
            size={16}
            className={isLiked ? "fill-primary text-primary" : "text-gray-400"}
          />
        </button>
        <div className="absolute bottom-2 left-2 px-2 py-0.5 bg-white/90 backdrop-blur rounded-md text-xs font-medium text-secondary">
          {product.scale}
        </div>
        {/* 稀缺标签 */}
        <div className={`absolute top-2 left-2 px-2 py-0.5 rounded-md text-xs font-bold ${rarity.color}`}>
          {rarity.label}
        </div>
        {/* 限量标识 */}
        {product.isLimited === 1 && (
          <div className="absolute bottom-2 right-2 px-2 py-0.5 bg-amber-500 text-white rounded-md text-xs font-bold">
            限量
          </div>
        )}
      </div>
      <div className="p-3">
        <h3 className="font-medium text-sm text-text-primary line-clamp-1">{product.name}</h3>
        <p className="text-xs text-text-secondary mt-0.5">{product.brand} · {product.series}</p>
        <div className="flex items-center justify-between mt-2">
          <span className="text-primary font-bold">¥{product.price.toLocaleString()}</span>
          <div className="flex items-center gap-2">
            {/* 价格趋势 */}
            <div className={`flex items-center gap-0.5 ${trend.color}`}>
              <TrendIcon size={12} />
              <span className="text-xs">{product.priceTrend || '稳定'}</span>
            </div>
            <div className="flex items-center gap-1 text-text-secondary">
              <Heart size={12} />
              <span className="text-xs">{product.likes || 0}</span>
            </div>
          </div>
        </div>
        {/* 市场价格范围 */}
        {hasMarketPrice && (
          <p className="text-xs text-text-secondary mt-1">
            市场价: ¥{product.marketPriceLow}-{product.marketPriceHigh}
          </p>
        )}
      </div>
    </motion.div>
  )
}
