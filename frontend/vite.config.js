import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { globSync } from "glob";

export default defineConfig({
  plugins: [tailwindcss(), react()],
  base: "/static/react_app/",
  build: {
    outDir: "../meal_planner_app/static/react_app",
    assetsDir: "assets",
    emptyOutDir: true,
    rollupOptions: {
      external: globSync("e2e/**"),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
});
