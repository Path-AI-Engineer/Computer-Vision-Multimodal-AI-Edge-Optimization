import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  base: "/app/",
  server: {
    port: 5174,
    proxy: {
      "/v1": "http://127.0.0.1:8024",
      "/health": "http://127.0.0.1:8024",
      "/ready": "http://127.0.0.1:8024",
      "/assets/samples": "http://127.0.0.1:8024"
    }
  }
});
