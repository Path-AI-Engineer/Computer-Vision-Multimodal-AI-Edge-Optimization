import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/app/",
  server: {
    proxy: {
      "/v1": "http://127.0.0.1:8022",
      "/health": "http://127.0.0.1:8022",
      "/ready": "http://127.0.0.1:8022",
      "/assets/samples": "http://127.0.0.1:8022"
    }
  }
});
