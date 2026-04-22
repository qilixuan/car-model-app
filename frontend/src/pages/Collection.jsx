import { motion } from 'framer-motion'
import { TrendingUp, Package, DollarSign } from 'lucide-react'
import CollectionCard from '../components/CollectionCard'
import useStore from '../store/useStore'

export default function Collection() {
  const { collections, getCollectionStats } = useStore()
  const stats = getCollectionStats()

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 bg-background/95 backdrop-blur-lg z-40 px-4 pt-4 pb-3">
        <h1 className="text-xl font-bold text-secondary">我的收藏</h1>
      </div>

      {/* Stats Cards */}
      <div className="px-4 mt-2 space-y-3">
        <div className="grid grid-cols-3 gap-2">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl p-3 shadow-sm"
          >
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
              <Package size={16} className="text-primary" />
            </div>
            <p className="text-xl font-bold text-secondary">{stats.total}</p>
            <p className="text-xs text-text-secondary">收藏总数</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="bg-white rounded-2xl p-3 shadow-sm"
          >
            <div className="w-8 h-8 rounded-lg bg-success/10 flex items-center justify-center mb-2">
              <DollarSign size={16} className="text-success" />
            </div>
            <p className="text-xl font-bold text-secondary">¥{(stats.totalValue / 1000).toFixed(1)}k</p>
            <p className="text-xs text-text-secondary">当前估值</p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl p-3 shadow-sm"
          >
            <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center mb-2">
              <TrendingUp size={16} className="text-warning" />
            </div>
            <p className={`text-xl font-bold ${stats.profit >= 0 ? 'text-success' : 'text-error'}`}>
              {stats.profit >= 0 ? '+' : ''}{stats.profit >= 0 ? '' : ''}{Math.abs(stats.profit) >= 0 ? '+' : ''}{(stats.profit / 1000).toFixed(1)}k
            </p>
            <p className="text-xs text-text-secondary">累计收益</p>
          </motion.div>
        </div>

        {/* Value Chart Placeholder */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-white rounded-2xl p-4 shadow-sm"
        >
          <p className="text-sm font-medium text-secondary mb-3">收藏价值走势</p>
          <div className="h-24 flex items-end gap-1">
            {[40, 55, 45, 70, 65, 80, 75, 90, 85, 95, 88, 100].map((h, i) => (
              <div
                key={i}
                className="flex-1 rounded-t-sm bg-gradient-to-t from-primary to-primary/60"
                style={{ height: `${h}%` }}
              />
            ))}
          </div>
          <div className="flex justify-between mt-2 text-xs text-text-secondary">
            <span>1月</span>
            <span>12月</span>
          </div>
        </motion.div>
      </div>

      {/* Collection Grid */}
      <div className="px-4 mt-4 pb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-bold text-secondary">我的车模</h2>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {collections.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
            >
              <CollectionCard item={item} />
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}
