import { expect, test } from "@playwright/test";

test("runs a qualification inference and exposes evidence", async ({ page }) => {
  await page.goto(".");
  await expect(page.getByRole("heading", { name: "Optimize the cost. Protect the signal." })).toBeVisible();
  await page.getByRole("button", { name: "Run sample inference" }).click();
  await expect(page.getByRole("heading", { name: "Inspect a prediction. Then inspect its cost." })).toBeVisible();
  await page.getByRole("button", { name: /edge-001/i }).click();
  await page.getByRole("button", { name: "Run qualification inference" }).click();
  await expect(page.getByRole("heading", { name: "abyssinian" })).toBeVisible();
  await page.getByRole("button", { name: /Evidence room/ }).click();
  await expect(page.getByRole("heading", { name: "Audit the environment. Read the failures." })).toBeVisible();
  await expect(page.getByText("Host CPU is not an edge device")).toBeVisible();
});

test("mobile navigation opens without horizontal overflow", async ({ page }) => {
  test.skip(test.info().project.name !== "mobile-chromium", "mobile-only contract");
  await page.goto(".");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("button", { name: /Benchmark matrix/ }).click();
  await expect(page.getByRole("heading", { name: "Compare what changed. Keep what did not." })).toBeVisible();
  const overflows = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
  expect(overflows).toBe(false);
});
