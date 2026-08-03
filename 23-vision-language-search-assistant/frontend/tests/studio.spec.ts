import { expect, test } from "@playwright/test";

test("completes an evidence-grounded retrieval and navigates system evidence", async ({ page }) => {
  await page.goto(".");
  await expect(page.getByRole("heading", { name: /Find the frame/i })).toBeVisible();

  await page.getByRole("textbox", { name: "Describe an observable scene" }).fill("red bicycle beside a brick wall");
  await page.getByRole("button", { name: /^Search/ }).click();

  await expect(page.getByText("vl-001").first()).toBeVisible();
  await expect(page.getByText("Qualification online")).toBeVisible();

  await page.getByRole("button", { name: /Benchmark/ }).click();
  await expect(page.getByRole("heading", { name: /Compare the method/i })).toBeVisible();
  await expect(page.getByText("Qualification only")).toBeVisible();

  await page.getByRole("button", { name: /System cards/ }).click();
  await expect(page.getByRole("heading", { name: /Know what produced/i })).toBeVisible();
  await expect(page.getByText("LOCKED_NOT_ACQUIRED").first()).toBeVisible();
});

test("mobile navigation remains keyboard and pointer accessible", async ({ page }) => {
  test.skip(test.info().project.name !== "mobile-chromium", "mobile-only contract");
  await page.goto(".");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("button", { name: /Failure atlas/ }).click();
  await expect(page.getByRole("heading", { name: /Failure is part/i })).toBeVisible();
});
