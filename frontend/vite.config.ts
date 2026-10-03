import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import path from "path"
import tailwindcss from "@tailwindcss/vite"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
  build: {
    target: 'esnext',
    minify: 'esbuild',
    cssMinify: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react') || id.includes('react-dom') || id.includes('react-router-dom')) return 'vendor';
            if (id.includes('lucide-react') || id.includes('framer-motion')) return 'ui';
            if (id.includes('zustand') || id.includes('@tanstack/react-query') || id.includes('axios')) return 'state';
          }
        },
      },
    },
  },
})
