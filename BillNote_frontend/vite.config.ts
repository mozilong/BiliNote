import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 先从本地 .env 加载，再回退到父目录的 .env
  const localEnv = loadEnv(mode, process.cwd(), '')
  const parentEnv = loadEnv(mode, process.cwd() + '/../', '')

  const apiBaseUrl = localEnv.VITE_API_BASE_URL || parentEnv.VITE_API_BASE_URL || 'http://localhost:8000'
  const port = parseInt(localEnv.VITE_FRONTEND_PORT || parentEnv.VITE_FRONTEND_PORT || '3015', 10)

  return {
    base: './',
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: port,
      allowedHosts: true, // 允许任意域名访问
      proxy: {
        '/api': {
          target: apiBaseUrl,
          changeOrigin: true,
          ws: true,
          secure: false,
        },
        '/static': {
          target: apiBaseUrl,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  }
})
