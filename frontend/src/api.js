const BASE_URL = "http://localhost:8000"

async function request(path, options = {}) {
  const token = localStorage.getItem("token")
  const headers = { "Content-Type": "application/json", ...options.headers }
  if (token) headers["Authorization"] = `Bearer ${token}`
  
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (res.status === 401) {
    localStorage.removeItem("token")
    window.location.href = "/login"
    return null
  }
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export const api = {
  // Auth
  login: (phone, name) => request("/api/auth/login", { method: "POST", body: JSON.stringify({ phone, name }) }),
  me: () => request("/api/auth/me"),
  
  // Products
  getProducts: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/api/products${qs ? "?" + qs : ""}`)
  },
  getProduct: (id) => request(`/api/products/${id}`),
  createProduct: (data) => request("/api/products", { method: "POST", body: JSON.stringify(data) }),
  likeProduct: (id) => request(`/api/products/${id}/like`, { method: "POST" }),
  
  // Collections
  getCollections: () => request("/api/collections"),
  createCollection: (data) => request("/api/collections", { method: "POST", body: JSON.stringify(data) }),
  deleteCollection: (id) => request(`/api/collections/${id}`, { method: "DELETE" }),
  
  // Chat
  getRooms: () => request("/api/chat/rooms"),
  createRoom: (productId) => request("/api/chat/rooms", { method: "POST", body: JSON.stringify({ product_id: productId }) }),
  getMessages: (roomId) => request(`/api/chat/rooms/${roomId}/messages`),
  sendMessage: (roomId, content) => request(`/api/chat/rooms/${roomId}/messages`, { method: "POST", body: JSON.stringify({ content }) }),
  
  // Market
  getTrending: () => request("/api/market/trending"),
  getBrandPrice: (brand) => request(`/api/market/price/${encodeURIComponent(brand)}`),
}
