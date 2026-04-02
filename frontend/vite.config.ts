import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/',
  server: {
    port: 5173,
    strictPort: true,
    host: '0.0.0.0', // 监听所有网络接口
    open: false,
    watch: {
      usePolling: true
    }
  }
})
