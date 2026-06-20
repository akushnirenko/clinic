import axios from 'axios'

const api = axios.create({
  // This matches your Vite proxy rule prefix (/api)
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Automatically attach the JWT token to every request if it exists in browser memory
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
