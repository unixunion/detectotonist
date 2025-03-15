import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
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
      "/api": {
        target: "http://127.0.0.1:8080", // 🔥 Flask server
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""), // 🔥 Removes `/api` prefix
      },
    },
  },
  // esbuild: {
  //   target: "esnext",
  // },
})
