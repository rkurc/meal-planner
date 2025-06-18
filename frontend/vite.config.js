// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/static/react_app/', // Important for asset paths
  build: {
    outDir: '../meal_planner_app/static/react_app', // Output to Flask's static folder
    assetsDir: 'assets', // Keep assets in an 'assets' subfolder within outDir
    emptyOutDir: true, // Clean the output directory before each build
  }
})
