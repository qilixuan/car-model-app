import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { TrendingUp, TrendingDown } from "lucide-react"
import { useNavigate } from "react-router-dom"

const mockTrendData = {
  "AutoWorld": { avgPrice: 1280, change: 5.2, history: [1100, 1150, 1080, 1200, 1220, 1280] },
  "ISO": { avgPrice: 2180, change: 12.5, history: [1800, 1900, 1950, 2000, 2100, 2180] },
  "合金变奏": { avgPrice: 680, change: -2.1, history: [720, 700, 690, 710, 695, 680] },
  "Tommy教父": { avgPrice: 1580, change: 8.3, history: [1400, 1450, 1500, 1520, 1550, 1580] },
  "LCD": { avgPrice: 1880, change: 3.7, history: [1700, 1750, 1780, 1820, 1850, 1880] },
  "UTO": { avgPrice: 2680, change: 15.2, history: [2200, 2300, 2400, 2500, 2600, 2680] },
}

export default function PriceTrend() {
  const navigate = useNavigate()
  const [selectedBrand, setSelectedBrand] = useState("AutoWorld")
  const [data, setData] = useState(mockTrendData)

  const current = data[selectedBrand]
  const maxPrice = Math.max(...current.history)
  const minPrice = Math.min(...current.history)

  return (
    <div className="min-h-screen bg-background pb-8">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-lg z-40 px-4 pt-4 pb-3">
        <h1 className="text-xl font-bold text-secondary">价格行情</h1>
      </div>

      {/* Brand Tabs */}
      <div className="px-4 mt-2">
        <div className="flex gap-2 overflow-x-auto hide-scrollbar pb-2">
          {Object.keys(data).map(brand => (
            <button
              key={brand}
              onClick={() => setSelectedBrand(brand)}
              className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                selectedBrand === brand
                  ? "bg-primary text-white"
                  : "bg-white border border-gray-100 text-text-secondary"
              }`}
            >
              {brand}
            </button>
          ))}
        </div>
      </div>

      {/* Price Card */}
      <div className="px-4 mt-4">
        <motion.div
          key={selectedBrand}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl p-5 shadow-sm"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-text-secondary text-sm">{selectedBrand}</p>
              <p className="text-3xl font-bold text-secondary mt-1">¥{current.avgPrice.toLocaleString()}</p>
            </div>
            <div className={`flex items-center gap-1 px-3 py-1.5 rounded-lg ${current.change >= 0 ? "bg-success/10" : "bg-error/10"}`}>
              {current.change >= 0 ? <TrendingUp size={16} className="text-success" /> : <TrendingDown size={16} className="text-error" />}
              <span className={`text-sm font-medium ${current.change >= 0 ? "text-success" : "text-error"}`}>
                {current.change >= 0 ? "+" : ""}{current.change}%
              </span>
            </div>
          </div>

          {/* Mini Chart */}
          <div className="h-32 flex items-end gap-2">
            {current.history.map((price, i) => {
              const height = ((price - minPrice) / (maxPrice - minPrice)) * 80 + 20
              const isUp = price >= current.history[0]
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: `${height}%` }}
                    transition={{ delay: i * 0.05, duration: 0.3 }}
                    className={`w-full rounded-t-sm ${isUp ? "bg-primary" : "bg-error/60"}`}
                  />
                  <span className="text-xs text-text-secondary">¥{(price/1000).toFixed(1)}k</span>
                </div>
              )
            })}
          </div>
          <p className="text-center text-xs text-text-secondary mt-2">近6个月价格走势</p>
        </motion.div>
      </div>

      {/* Range */}
      <div className="px-4 mt-4">
        <div className="bg-white rounded-2xl p-4 shadow-sm">
          <div className="flex justify-between text-sm">
            <div className="text-center">
              <p className="text-text-secondary">最低价</p>
              <p className="font-bold text-secondary mt-1">¥{minPrice.toLocaleString()}</p>
            </div>
            <div className="w-px bg-gray-100" />
            <div className="text-center">
              <p className="text-text-secondary">最高价</p>
              <p className="font-bold text-secondary mt-1">¥{maxPrice.toLocaleString()}</p>
            </div>
            <div className="w-px bg-gray-100" />
            <div className="text-center">
              <p className="text-text-secondary">当前</p>
              <p className="font-bold text-primary mt-1">¥{current.avgPrice.toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Other Brands */}
      <div className="px-4 mt-4">
        <h2 className="text-lg font-bold text-secondary mb-3">热门品牌</h2>
        <div className="space-y-2">
          {Object.entries(data)
            .filter(([brand]) => brand !== selectedBrand)
            .map(([brand, info], i) => (
              <motion.div
                key={brand}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="bg-white rounded-xl p-4 shadow-sm flex items-center justify-between"
              >
                <div>
                  <p className="font-medium text-secondary">{brand}</p>
                  <p className="text-sm text-text-secondary mt-0.5">¥{info.avgPrice.toLocaleString()}</p>
                </div>
                <div className={`flex items-center gap-1 ${info.change >= 0 ? "text-success" : "text-error"}`}>
                  {info.change >= 0 ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                  <span className="text-sm font-medium">{info.change >= 0 ? "+" : ""}{info.change}%</span>
                </div>
              </motion.div>
            ))}
        </div>
      </div>
    </div>
  )
}
