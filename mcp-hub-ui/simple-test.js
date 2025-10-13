// Simple Playwright test to verify installation
const { test, expect } = require('@playwright/test');

test('basic test', async ({ page }) => {
  await page.goto('http://localhost:3001');
  await expect(page).toHaveTitle(/MCP Hub/);
});
