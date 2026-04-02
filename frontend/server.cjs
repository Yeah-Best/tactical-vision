const { createServer } = require('vite')
const vue = require('@vitejs/plugin-vue')

async function startServer() {
  const server = await createServer({
    plugins: [vue()],
    server: {
      port: 5173,
      strictPort: true,
      host: '127.0.0.1', // 强制 IPv4
      watch: {
        usePolling: true
      }
    }
  })

  await server.listen()
  console.log('\n====================================')
  console.log('  战术视界 - 前端开发服务器')
  console.log('====================================')
  console.log('\n访问地址:')
  console.log('  - http://localhost:5173')
  console.log('  - http://127.0.0.1:5173')
  console.log('  - http://192.168.192.1:5173 (网络访问)')
  console.log('\n按 Ctrl+C 停止服务')
  console.log('====================================\n')
}

startServer()
