import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [tailwindcss(), react()],
  base: '/static/react_app/',
  build: {
    outDir: '../meal_planner_app/static/react_app',
    assetsDir: 'assets',
    emptyOutDir: true,
  },
});
