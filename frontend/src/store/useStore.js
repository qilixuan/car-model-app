import { create } from 'zustand'
import { mockProducts, mockCollections } from '../data/mockData'

const useStore = create((set, get) => ({
  // 用户
  user: { name: "藏家小王", avatar: null, phone: "139****9923", rating: 4.8 },
  
  // 商品列表
  products: mockProducts,
  filterProducts: (filters) => {
    const { products } = get()
    return products.filter(p => {
      if (filters.brand && filters.brand !== "全部" && p.brand !== filters.brand) return false
      if (filters.scale && filters.scale !== "全部" && p.scale !== filters.scale) return false
      if (filters.condition && filters.condition !== "全部" && p.condition !== filters.condition) return false
      if (filters.material && filters.material !== "全部" && p.material !== filters.material) return false
      if (filters.minPrice && p.price < filters.minPrice) return false
      if (filters.maxPrice && p.price > filters.maxPrice) return false
      return true
    })
  },
  
  // 收藏
  collections: mockCollections,
  addCollection: (item) => set(state => ({
    collections: [...state.collections, { ...item, id: Date.now() }]
  })),
  removeCollection: (id) => set(state => ({
    collections: state.collections.filter(c => c.id !== id)
  })),
  getCollectionStats: () => {
    const { collections } = get()
    const total = collections.length
    const totalValue = collections.reduce((sum, c) => sum + c.currentValue, 0)
    const totalCost = collections.reduce((sum, c) => sum + c.purchasePrice, 0)
    return { total, totalValue, totalCost, profit: totalValue - totalCost }
  },
  
  // 喜欢的商品
  likedProducts: [],
  toggleLike: (id) => set(state => ({
    likedProducts: state.likedProducts.includes(id)
      ? state.likedProducts.filter(pid => pid !== id)
      : [...state.likedProducts, id]
  })),
  
  // 发布的商品
  myProducts: [],
  addProduct: (product) => set(state => ({
    myProducts: [...state.myProducts, { ...product, id: Date.now(), seller: state.user }]
  })),
}))

export default useStore
