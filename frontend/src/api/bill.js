import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

api.interceptors.response.use(
  response => response.data,
  error => {
    const errorMsg = error.response?.data?.error || error.message || '请求失败'
    return Promise.reject(new Error(errorMsg))
  }
)

export const uploadFile = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getRecords = (params) => api.get('/records', { params })
export const updateRecord = (id, data) => api.put(`/records/${id}`, data)
export const getCategories = () => api.get('/categories')
export const getStats = () => api.get('/stats')
export const exportExcel = () => api.get('/export', { responseType: 'blob' })
export const clearRecords = () => api.post('/clear')
