import { TrendingUp, TrendingDown } from 'lucide-react'
import { motion } from 'framer-motion'

export default function CollectionCard({ item }) {
  const profit = item.currentValue - item.purchasePrice
  const profitRate = ((profit / item.purchasePrice) * 100).toFixed(1)
  const isUp = profit >= 0

  return (
    <motion.div
      whileTap={{ scale: 0.97 }}
      className="bg-surface rounded-2xl overflow-hidden shadow-sm cursor-pointer"
    >
      <div className="relative aspect-square bg-gray-100">
        <img
          src={item.image}
          alt={item.name}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        <div className="absolute top-2 left-2 px-2 py-0.5 bg-secondary/80 backdrop-blur rounded-md text-xs font-medium text-white">
          {item.scale}
        </div>
      </div>
      <div className="p-3">
        <h3 className="font-medium text-sm text-text-primary line-clamp-1">{item.name}</h3>
        <div className="flex items-center gap-1 mt-1">
          <span className="text-xs text-text-secondary">入手</span>
          <span className="text-xs text-primary font-medium">¥{item.purchasePrice}</span>
        </div>
        <div className="flex items-center justify-between mt-2">
          <span className="text-sm font-bold text-text-primary">¥{item.currentValue.toLocaleString()}</span>
          <div className={`flex items-center gap-0.5 px-1.5 py-0.5 rounded-md ${isUp ? 'bg-success/10' : 'bg-error/10'}`}>
            {isUp ? <TrendingUp size={12} className="text-success" /> : <TrendingDown size={12} className="text-error" />}
            <span className={`text-xs font-medium ${isUp ? 'text-success' : 'text-error'}`}>{profitRate}%</span>
          </div>
        </div>
        <p className="text-xs text-text-secondary mt-2">{item.purchaseDate} 入库</p>
      </div>
    </motion.div>
  )
}
