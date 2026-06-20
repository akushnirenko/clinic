 import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  // Load env variables ( .env .env.development .env.production )
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      vue(),
      vueDevTools(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    server: {
      proxy: {
        '/api': {
          // FIX: If env.VITE_API_BASE_URL is relative "/api", fallback to localhost:8000 for safety
          target: env.VITE_API_BASE_URL === '/api' ? 'http://localhost:8000' : env.VITE_API_BASE_URL,
          changeOrigin: true,
        },
      },
    },
  }
})
