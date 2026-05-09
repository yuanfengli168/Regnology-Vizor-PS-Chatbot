import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Base path must match the GitHub repo name for GitHub Pages
export default defineConfig({
  plugins: [react()],
  base: '/Regnology-Vizor-PS-Chatbot/',
})
