import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
    plugins: [react()],
    base: "/app/",
    server: {
        port: 5173,
        proxy: {
            "/v1": "http://127.0.0.1:8023",
            "/health": "http://127.0.0.1:8023",
            "/ready": "http://127.0.0.1:8023",
            "/assets/corpus": "http://127.0.0.1:8023"
        }
    }
});
