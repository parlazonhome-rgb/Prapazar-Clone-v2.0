import axios from 'axios'
import { useAuthStore } from '../store/authStore'

// Production'da Render URL, development'ta localhost
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - token ekle
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - hata yönetimi
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  register: (data: any) =>
    api.post('/auth/register', data),
  me: () =>
    api.get('/auth/me'),
}

// Products API
export const productApi = {
  list: (params?: any) =>
    api.get('/products', { params }),
  get: (id: number) =>
    api.get(`/products/${id}`),
  create: (data: any) =>
    api.post('/products', data),
  update: (id: number, data: any) =>
    api.put(`/products/${id}`, data),
  delete: (id: number) =>
    api.delete(`/products/${id}`),
  importExcel: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/products/import-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  sync: (productId: number, storeId: number) =>
    api.post(`/products/${productId}/sync/${storeId}`),
}

// Orders API
export const orderApi = {
  list: (params?: any) =>
    api.get('/orders', { params }),
  get: (id: number) =>
    api.get(`/orders/${id}`),
  stats: () =>
    api.get('/orders/stats'),
  today: () =>
    api.get('/orders/today'),
  updateStatus: (id: number, data: any) =>
    api.put(`/orders/${id}`, data),
  shipment: (id: number, data: any) =>
    api.post(`/orders/${id}/shipment`, data),
  cancel: (id: number) =>
    api.post(`/orders/${id}/cancel`),
}

// Stores API
export const storeApi = {
  list: () =>
    api.get('/stores'),
  create: (data: any) =>
    api.post('/stores', data),
  update: (id: number, data: any) =>
    api.put(`/stores/${id}`, data),
  delete: (id: number) =>
    api.delete(`/stores/${id}`),
  testConnection: (id: number) =>
    api.post(`/stores/${id}/test-connection`),
  sync: (id: number) =>
    api.post(`/stores/${id}/sync`),
}

// Categories API
export const categoryApi = {
  list: () =>
    api.get('/categories'),
  create: (data: any) =>
    api.post('/categories', data),
  update: (id: number, data: any) =>
    api.put(`/categories/${id}`, data),
  delete: (id: number) =>
    api.delete(`/categories/${id}`),
}
