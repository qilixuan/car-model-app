import { useState, useEffect } from 'react'
import { Filter, SlidersHorizontal } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import ProductCard from '../components/ProductCard'
import useStore from '../store/useStore'

export default function Market() {
  const { filterProducts, fetchProducts, productsLoading } = useStore()
  const [showFilter, setShowFilter] = useState(false)
  const [filters, setFilters] = useState({ brand: "全部", scale: "全部", condition: "全部", material: "全部" })
  const [sortBy, setSortBy] = useState("latest")

  // 加载商品数据
  useEffect(() => {
    fetchProducts({ sort: sortBy, ...filters })
  }, [])

  const filtered = filterProducts({ ...filters, sort: sortBy })

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === "price-low") return a.price - b.price
    if (sortBy === "price-high") return b.price - a.price
    if (sortBy === "popular") return b.likes - a.likes
    return new Date(b.postedAt) - new Date(a.postedAt)
  })

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-lg z-40 px-4 pt-4 pb-2">
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-xl font-bold text-secondary">交易市场</h1>
          <button
            onClick={() => setShowFilter(!showFilter)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white border border-gray-100 text-sm"
          >
            <SlidersHorizontal size={14} />
            <span className="text-text-secondary">筛选</span>
          </button>
        </div>

        {/* Filter Chips */}
        <div className="flex gap-2 overflow-x-auto hide-scrollbar pb-2">
          {["最新", "价格低", "价格高", "最热"].map((tab, i) => (
            <button
              key={tab}
              onClick={() => { setSortBy(["latest", "price-low", "price-high", "popular"][i]); fetchProducts({ ...filters, sort: ["latest", "price-low", "price-high", "popular"][i] }) }}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                sortBy === ["latest", "price-low", "price-high", "popular"][i]
                  ? 'bg-primary text-white'
                  : 'bg-white border border-gray-100 text-text-secondary'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Filter Panel */}
      <AnimatePresence>
        {showFilter && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 py-4 bg-white border-b border-gray-100 space-y-4">
              {[
                { label: "品牌", options: brands },
                { label: "比例", options: scales },
                { label: "成色", options: conditions },
                { label: "材质", options: materials },
              ].map(({ label, options }) => (
                <div key={label}>
                  <p className="text-sm font-medium text-text-secondary mb-2">{label}</p>
                  <div className="flex flex-wrap gap-2">
                    {options.map(opt => (
                      <button
                        key={opt}
                        onClick={() => setFilters(prev => ({ ...prev, [label]: opt }))}
                        className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                          filters[label.toLowerCase()] === opt || (label === "品牌" && filters.brand === opt) || (label === "比例" && filters.scale === opt) || (label === "成色" && filters.condition === opt) || (label === "材质" && filters.material === opt)
                            ? 'bg-primary text-white'
                            : 'bg-gray-100 text-text-secondary'
                        }`}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setFilters({ brand: "全部", scale: "全部", condition: "全部", material: "全部" })}
                  className="flex-1 h-10 rounded-xl border border-gray-200 text-text-secondary text-sm"
                >
                  重置
                </button>
                <button
                  onClick={() => setShowFilter(false)}
                  className="flex-1 h-10 rounded-xl bg-primary text-white text-sm font-medium"
                >
                  确定
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Product Grid */}
      <div className="px-4 py-4">
        <p className="text-sm text-text-secondary mb-3">共 {sorted.length} 件商品</p>
        <div className="grid grid-cols-2 gap-3">
          {sorted.map((product, i) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.04 }}
            >
              <ProductCard product={product} />
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
