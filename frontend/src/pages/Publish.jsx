import { useState } from 'react'
import { Camera, X, ChevronRight } from 'lucide-react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import useStore from '../store/useStore'

const scales = ["1:18", "1:43", "1:64", "其他"]
const conditions = ["全新", "几乎全新", "轻微瑕疵", "明显瑕疵"]

export default function Publish() {
  const navigate = useNavigate()
  const { addProduct } = useStore()
  const [images, setImages] = useState([])
  const [form, setForm] = useState({
    name: "", brand: "", condition: "", price: "", description: "", scale: "1:18"
  })
  const [step, setStep] = useState(1)

  const handleImagePick = () => {
    // 模拟添加图片
    const newImg = `https://picsum.photos/400/400?random=${Date.now()}`
    if (images.length < 6) setImages([...images, newImg])
  }

  const handlePublish = () => {
    if (!form.name || !form.price || images.length === 0) return
    addProduct({
      ...form,
      images,
      originalPrice: form.price,
      likes: 0,
      views: 0,
      postedAt: new Date().toISOString().split("T")[0],
    })
    navigate("/collection")
  }

  if (step === 1) {
    return (
      <div className="min-h-screen bg-background">
        <div className="sticky top-0 bg-background/95 backdrop-blur-lg z-40 px-4 pt-4 pb-3 border-b border-gray-100">
          <h1 className="text-xl font-bold text-secondary">发布宝贝</h1>
        </div>
        <div className="p-4 space-y-4">
          {/* Image Upload */}
          <div className="grid grid-cols-3 gap-2">
            {images.map((img, i) => (
              <motion.div key={i} className="aspect-square rounded-xl overflow-hidden relative bg-gray-100">
                <img src={img} alt="" className="w-full h-full object-cover" />
                <button
                  onClick={() => setImages(images.filter((_, idx) => idx !== i))}
                  className="absolute top-1 right-1 w-5 h-5 rounded-full bg-black/50 flex items-center justify-center"
                >
                  <X size={12} className="text-white" />
                </button>
              </motion.div>
            ))}
            {images.length < 6 && (
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={handleImagePick}
                className="aspect-square rounded-xl border-2 border-dashed border-gray-200 flex flex-col items-center justify-center gap-1 bg-gray-50"
              >
                <Camera size={24} className="text-text-secondary" />
                <span className="text-xs text-text-secondary">{images.length}/6</span>
              </motion.button>
            )}
          </div>

          {/* Info Form */}
          <div className="space-y-3">
            {[
              { key: "name", label: "名称", placeholder: "品牌+系列+车型" },
              { key: "brand", label: "品牌", placeholder: "如 AutoWorld" },
            ].map(({ key, label, placeholder }) => (
              <div key={key}>
                <p className="text-sm text-text-secondary mb-1.5">{label}</p>
                <input
                  type="text"
                  placeholder={placeholder}
                  value={form[key]}
                  onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  className="w-full h-11 px-4 rounded-xl bg-white border border-gray-100 text-sm focus:outline-none focus:border-primary"
                />
              </div>
            ))}

            {/* Scale */}
            <div>
              <p className="text-sm text-text-secondary mb-1.5">比例</p>
              <div className="flex gap-2">
                {scales.map(s => (
                  <button
                    key={s}
                    onClick={() => setForm({ ...form, scale: s })}
                    className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                      form.scale === s ? 'bg-primary text-white' : 'bg-white border border-gray-100 text-text-secondary'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Condition */}
            <div>
              <p className="text-sm text-text-secondary mb-1.5">成色</p>
              <div className="flex gap-2">
                {conditions.map(c => (
                  <button
                    key={c}
                    onClick={() => setForm({ ...form, condition: c })}
                    className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                      form.condition === c ? 'bg-primary text-white' : 'bg-white border border-gray-100 text-text-secondary'
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            {/* Price */}
            <div>
              <p className="text-sm text-text-secondary mb-1.5">售价</p>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-text-primary font-medium">¥</span>
                <input
                  type="number"
                  placeholder="0"
                  value={form.price}
                  onChange={(e) => setForm({ ...form, price: e.target.value })}
                  className="w-full h-11 pl-8 pr-4 rounded-xl bg-white border border-gray-100 text-sm focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            {/* Description */}
            <div>
              <p className="text-sm text-text-secondary mb-1.5">描述</p>
              <textarea
                placeholder="补充说明（成色细节、配件情况等）"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={3}
                className="w-full p-4 rounded-xl bg-white border border-gray-100 text-sm focus:outline-none focus:border-primary resize-none"
              />
            </div>
          </div>

          <motion.button
            whileTap={{ scale: 0.98 }}
            onClick={handlePublish}
            disabled={!form.name || !form.price || images.length === 0}
            className="w-full h-12 rounded-xl bg-gradient-to-r from-primary to-primary-dark text-white font-semibold shadow-lg shadow-primary/30 disabled:opacity-50 mt-4"
          >
            发布宝贝
          </motion.button>
        </div>
      </div>
    )
  }

  return null
}
