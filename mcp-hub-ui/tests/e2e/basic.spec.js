// Basic Playwright test
const { test, expect } = require('@playwright/test');

test.describe('Basic MCP Hub Tests', () => {
  test('should load the homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/MCP Hub/);
    
    // Check for main content
    await expect(page.locator('body')).toContainText(['Dashboard', 'System Status']);
  });

  test('should navigate to chat page', async ({ page }) => {
    await page.goto('/');
    
    // Click on chat navigation
    await page.click('a[href="/chat"]');
    await expect(page).toHaveURL(/.*\/chat/);
    
    // Check for chat content
    await expect(page.locator('body')).toContainText(['Chat', 'Messages']);
  });

  test('should navigate to tools page', async ({ page }) => {
    await page.goto('/');
    
    // Click on tools navigation
    await page.click('a[href="/tools"]');
    await expect(page).toHaveURL(/.*\/tools/);
    
    // Check for tools content
    await expect(page.locator('body')).toContainText(['Tools', 'Available']);
  });

  test('should navigate to resources page', async ({ page }) => {
    await page.goto('/');
    
    // Click on resources navigation
    await page.click('a[href="/resources"]');
    await expect(page).toHaveURL(/.*\/resources/);
    
    // Check for resources content
    await expect(page.locator('body')).toContainText(['Resources', 'Database']);
  });

  test('should navigate to settings page', async ({ page }) => {
    await page.goto('/');
    
    // Click on settings navigation
    await page.click('a[href="/settings"]');
    await expect(page).toHaveURL(/.*\/settings/);
    
    // Check for settings content
    await expect(page.locator('body')).toContainText(['Settings', 'Configuration']);
  });
});
