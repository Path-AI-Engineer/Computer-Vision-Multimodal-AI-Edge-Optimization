import { expect, test } from "@playwright/test";

test("inspection lab exposes the real evidence workflow", async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /see the defect/i })).toBeVisible();
  await page.getByRole("button", { name: "Inspect surface" }).click();
  await expect(page.getByText(/probability/i).first()).toBeVisible();
  await page.keyboard.press("Tab");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  expect(overflow).toBeFalsy();
  expect(consoleErrors).toEqual([]);
});

test("reduced motion is respected", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const duration = await page.locator("body").evaluate((element) =>
    getComputedStyle(element).getPropertyValue("scroll-behavior")
  );
  expect(duration).not.toBe("smooth");
});
