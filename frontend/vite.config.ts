import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://backend:8000',
        ws: true,
      },
    },
  },
  build: {
    // Разбить бандл на чанки для ускорения загрузки
    rollupOptions: {
      output: {
        manualChunks: {
          // Тяжёлые библиотеки визуализации
          'vendor-xterm': ['@xterm/xterm', '@xterm/addon-fit', '@xterm/addon-web-links'],
          'vendor-d3': ['d3'],
          'vendor-md': ['@uiw/react-md-editor', '@uiw/react-markdown-preview'],
          // React-экосистема
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-query': ['@tanstack/react-query', 'zustand'],
          'vendor-motion': ['framer-motion'],
          // Прочее
          'vendor-misc': ['axios', 'cmdk', 'react-hot-toast', 'canvas-confetti'],
        },
      },
    },
    chunkSizeWarningLimit: 1800,
  },
})
