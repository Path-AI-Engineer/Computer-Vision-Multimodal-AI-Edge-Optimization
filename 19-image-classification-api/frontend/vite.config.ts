import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/v1": "http://127.0.0.1:8019",
      "/health": "http://127.0.0.1:8019",
      "/ready": "http://127.0.0.1:8019",
      "/samples": "http://127.0.0.1:8019",
      "/reports": "http://127.0.0.1:8019"
    }
  }
});
