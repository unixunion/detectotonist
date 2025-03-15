import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import { resolve } from 'path'

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
  build: {
    outDir: "../static/assets",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
      output: {
        assetFileNames: 'index.[ext]',
        entryFileNames: 'index.js',
      },
    },
  },
  publicDir: false,
  buildEnd: async () => {
    const fs = require('fs');
    const path = require('path');

    // Move index.html to ../templates after build
    const srcPath = path.resolve(__dirname, '../static/assets/index.html');
    const destPath = path.resolve(__dirname, '../templates/index.html');

    if (fs.existsSync(srcPath)) {
      fs.renameSync(srcPath, destPath);
      console.log("✅ Moved index.html to ../templates/");
    }
  }
})
