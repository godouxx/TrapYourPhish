import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "dist",
    rollupOptions: {
      input: {
        main: "index.html",
        connexion: "src/connexion.html",
        register: "src/register.html",
      },
    },
  },
});