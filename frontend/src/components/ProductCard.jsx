import { Heart } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import useStore from '../store/useStore'

export default function ProductCard({ product }) {
  const navigate = useNavigate()
  const { likedProducts, toggleLike } = useStore()
  const isLiked = likedProducts.includes(product.id)

  return (
    <motion.div
      whileTap={{ scale: 0.97 }}
      onClick={() => navigate(`/product/${product.id}`)}
      className="bg-surface rounded-2xl overflow-hidden shadow-sm cursor-pointer"
    >
      <div className="relative aspect-square bg-gray-100">
        <img
          src={product.images[0]}
          alt={product.name}
          className="w-full h-full object-cover"
          loading="lazy"
        />
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
      </div>
      <div className="p-3">
        <h3 className="font-medium text-sm text-text-primary line-clamp-1">{product.name}</h3>
        <p className="text-xs text-text-secondary mt-0.5">{product.brand} · {product.series}</p>
        <div className="flex items-center justify-between mt-2">
          <span className="text-primary font-bold">¥{product.price.toLocaleString()}</span>
          <div className="flex items-center gap-1 text-text-secondary">
            <Heart size={12} />
            <span className="text-xs">{product.likes}</span>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
