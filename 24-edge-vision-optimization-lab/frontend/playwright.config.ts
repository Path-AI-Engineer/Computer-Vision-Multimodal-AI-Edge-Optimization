import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  retries: 0,
  reporter: "line",
  use: { baseURL: "http://127.0.0.1:8024/app/", trace: "retain-on-failure" },
  webServer: {
    command: "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8024",
    cwd: "..",
    env: { PYTHONPATH: "." },
    url: "http://127.0.0.1:8024/ready",
    timeout: 120_000,
    reuseExistingServer: true
  },
  projects: [
    { name: "desktop-chromium", use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } } },
    { name: "mobile-chromium", use: { ...devices["iPhone 13"], viewport: { width: 390, height: 844 } } }
  ]
});
