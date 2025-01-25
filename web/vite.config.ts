import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: "0.0.0.0",
    open: false, //是否自动弹出浏览器页面
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:997',//这里填入你要请求的接口的前缀
        changeOrigin:true,//虚拟的站点需要更管origin
      }
    }
  },
})
