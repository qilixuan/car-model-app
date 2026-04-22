import { useState } from 'react'
import { Search, Bell } from 'lucide-react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import ProductCard from '../components/ProductCard'
import { mockProducts } from '../data/mockData'

const banners = [
  { id: 1, title: "新年特惠", subtitle: "精选车模8折起", color: "from-primary/90 to-primary-dark/90" },
  { id: 2, title: "限量发售", subtitle: "ISO 保时捷 911 GT3 RS", color: "from-accent/90 to-warning/90" },
  { id: 3, title: "社区热议", subtitle: "2024年度收藏榜单", color: "from-success/90 to-success-dark/90" },
]

export default function Home() {
  const navigate = useNavigate()
  const [searchValue, setSearchValue] = useState("")
  const [bannerIndex, setBannerIndex] = useState(0)

  const latestProducts = mockProducts.slice(0, 6)

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-lg z-40 px-4 pt-4 pb-2">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary" />
            <input
              type="text"
              placeholder="搜索品牌/系列/车型..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="w-full h-10 pl-10 pr-4 rounded-xl bg-white border border-gray-100 text-sm focus:outline-none focus:border-primary transition-colors"
            />
          </div>
          <button className="w-10 h-10 rounded-xl bg-white border border-gray-100 flex items-center justify-center relative">
            <Bell size={18} className="text-text-secondary" />
            <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary" />
          </button>
        </div>
      </div>

      {/* Banner */}
      <div className="px-4 mt-4">
        <div className="relative h-36 rounded-2xl overflow-hidden">
          <motion.div
            key={bannerIndex}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`absolute inset-0 bg-gradient-to-r ${banners[bannerIndex].color}`}
          />
          <div className="relative p-5 h-full flex flex-col justify-between">
            <div>
              <h2 className="text-white text-xl font-bold">{banners[bannerIndex].title}</h2>
              <p className="text-white/80 text-sm mt-1">{banners[bannerIndex].subtitle}</p>
            </div>
            <div className="flex gap-1.5">
              {banners.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setBannerIndex(i)}
                  className={`w-6 h-1.5 rounded-full transition-colors ${i === bannerIndex ? 'bg-white' : 'bg-white/40'}`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Hot Brands */}
      <div className="mt-6 px-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold text-secondary">热门品牌</h2>
          <button onClick={() => navigate('/market')} className="text-sm text-primary">查看全部</button>
        </div>
        <div className="flex gap-3 overflow-x-auto hide-scrollbar pb-2">
          {["AutoWorld", "ISO", "合金变奏", "Tommy教父", "LCD", "MiniGT"].map((brand, i) => (
            <motion.button
              key={brand}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/market')}
              className="flex-shrink-0 px-4 py-2 rounded-full bg-white border border-gray-100 text-sm font-medium text-secondary shadow-sm"
            >
              {brand}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Latest Products */}
      <div className="mt-6 px-4 pb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold text-secondary">最新上架</h2>
          <button onClick={() => navigate('/market')} className="text-sm text-primary">更多</button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {latestProducts.map((product, i) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
            >
              <ProductCard product={product} />
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
