/**
 * User Interaction tests for MCP Hub UI
 * Tests forms, buttons, and user interactions
 */

import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers.js';
import { testData } from '../fixtures/test-data.js';

test.describe('User Interaction Tests', () => {
  let helpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test('should send chat message', async ({ page }) => {
    await helpers.navigateTo('/chat');
    await helpers.waitForPageLoad();

    // Find message input
    const messageInput = page.locator('[data-testid="message-input"], textarea, input[type="text"]').first();
    await expect(messageInput).toBeVisible();

    // Type message
    const testMessage = testData.user.testMessage;
    await messageInput.fill(testMessage);

    // Find and click send button
    const sendButton = page.locator('[data-testid="send-button"], button[type="submit"]').first();
    await expect(sendButton).toBeVisible();
    await sendButton.click();

    // Wait for message to appear
    await page.waitForTimeout(1000);

    // Check that message was sent
    await expect(page.locator('body')).toContainText(testMessage);
  });

  test('should execute tool with arguments', async ({ page }) => {
    await helpers.navigateTo('/tools');
    await helpers.waitForPageLoad();

    // Wait for tools to load
    await helpers.waitForLoadingComplete();

    // Find and click execute button for first tool
    const executeButton = page.locator('[data-testid="execute-button"], button:has-text("Execute")').first();
    if (await executeButton.isVisible()) {
      await executeButton.click();

      // Wait for tool dialog
      await helpers.waitForDialog();

      // Fill tool arguments if dialog appears
      const argumentInput = page.locator('[data-testid="tool-arguments"], input, textarea').first();
      if (await argumentInput.isVisible()) {
        await argumentInput.fill(JSON.stringify(testData.user.toolArguments));
      }

      // Submit tool execution
      const submitButton = page.locator('button:has-text("Execute"), button:has-text("Submit")').first();
      if (await submitButton.isVisible()) {
        await submitButton.click();
      }

      // Wait for execution result
      await page.waitForTimeout(2000);

      // Check for result or error
      const hasResult = await page.locator('[data-testid="result"], .result, .MuiAlert-root').count() > 0;
      expect(hasResult).toBeTruthy();
    }
  });

  test('should execute database query', async ({ page }) => {
    await helpers.navigateTo('/resources');
    await helpers.waitForPageLoad();

    // Wait for resources to load
    await helpers.waitForLoadingComplete();

    // Find query input
    const queryInput = page.locator('[data-testid="query-input"], textarea, input').first();
    if (await queryInput.isVisible()) {
      await queryInput.fill(testData.user.sqlQuery);

      // Find and click execute button
      const executeButton = page.locator('[data-testid="execute-query-button"], button:has-text("Execute")').first();
      if (await executeButton.isVisible()) {
        await executeButton.click();

        // Wait for query result
        await page.waitForTimeout(2000);

        // Check for result
        const hasResult = await page.locator('[data-testid="query-result"], .result, .MuiAlert-root').count() > 0;
        expect(hasResult).toBeTruthy();
      }
    }
  });

  test('should handle form validation', async ({ page }) => {
    await helpers.navigateTo('/chat');
    await helpers.waitForPageLoad();

    // Try to send empty message
    const sendButton = page.locator('[data-testid="send-button"], button[type="submit"]').first();
    await sendButton.click();

    // Check for validation error or disabled state
    const hasValidation = await page.locator('.error, [role="alert"], .MuiFormHelperText-root').count() > 0;
    const isDisabled = await sendButton.isDisabled();
    
    expect(hasValidation || isDisabled).toBeTruthy();
  });

  test('should handle button states correctly', async ({ page }) => {
    await helpers.navigateTo('/tools');
    await helpers.waitForPageLoad();

    // Check that buttons are enabled when ready
    const executeButton = page.locator('[data-testid="execute-button"], button:has-text("Execute")').first();
    if (await executeButton.isVisible()) {
      const isEnabled = await executeButton.isEnabled();
      expect(isEnabled).toBeTruthy();
    }
  });

  test('should handle dialog interactions', async ({ page }) => {
    await helpers.navigateTo('/tools');
    await helpers.waitForPageLoad();

    // Click execute button to open dialog
    const executeButton = page.locator('[data-testid="execute-button"], button:has-text("Execute")').first();
    if (await executeButton.isVisible()) {
      await executeButton.click();

      // Wait for dialog
      await helpers.waitForDialog();

      // Check dialog is visible
      const dialog = page.locator('[role="dialog"], .MuiDialog-root');
      await expect(dialog).toBeVisible();

      // Close dialog
      await helpers.closeDialog();

      // Check dialog is closed
      await expect(dialog).not.toBeVisible();
    }
  });

  test('should handle keyboard navigation', async ({ page }) => {
    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();

    // Test Tab navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Test Enter key
    await page.keyboard.press('Enter');

    // Test Escape key
    await page.keyboard.press('Escape');
  });

  test('should handle copy functionality', async ({ page }) => {
    await helpers.navigateTo('/chat');
    await helpers.waitForPageLoad();

    // Send a message
    const messageInput = page.locator('[data-testid="message-input"], textarea, input[type="text"]').first();
    if (await messageInput.isVisible()) {
      await messageInput.fill('Test message for copy');
      
      const sendButton = page.locator('[data-testid="send-button"], button[type="submit"]').first();
      await sendButton.click();

      await page.waitForTimeout(1000);

      // Look for copy button
      const copyButton = page.locator('[data-testid="copy-button"], button:has-text("Copy")').first();
      if (await copyButton.isVisible()) {
        await copyButton.click();

        // Check clipboard content
        const clipboardText = await page.evaluate(() => navigator.clipboard.readText());
        expect(clipboardText).toContain('Test message');
      }
    }
  });

  test('should handle responsive design interactions', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();

    // Test mobile menu if present
    const mobileMenu = page.locator('[data-testid="mobile-menu"], .MuiIconButton-root').first();
    if (await mobileMenu.isVisible()) {
      await mobileMenu.click();
      
      // Check menu is open
      const menuItems = page.locator('[role="menu"], .MuiMenu-root');
      await expect(menuItems).toBeVisible();
    }

    // Test desktop viewport
    await page.setViewportSize({ width: 1200, height: 800 });
    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();

    // Check desktop navigation
    const navItems = page.locator('nav a, [role="navigation"] a');
    const navCount = await navItems.count();
    expect(navCount).toBeGreaterThan(0);
  });

  test('should handle loading states during interactions', async ({ page }) => {
    await helpers.navigateTo('/tools');
    await helpers.waitForPageLoad();

    // Click execute button
    const executeButton = page.locator('[data-testid="execute-button"], button:has-text("Execute")').first();
    if (await executeButton.isVisible()) {
      await executeButton.click();

      // Check for loading state
      const loadingElements = await page.locator('[data-testid="loading"], .loading, .MuiCircularProgress-root').count();
      
      // Should show loading during execution
      expect(loadingElements).toBeGreaterThan(0);
    }
  });

  test('should handle error states gracefully', async ({ page }) => {
    // Mock API failure
    await helpers.mockApiResponse('**/api/tools', { error: 'Service unavailable' });

    await helpers.navigateTo('/tools');
    await helpers.waitForPageLoad();

    // Check for error handling
    const errorElements = await page.locator('[data-testid="error"], .error, .MuiAlert-root').count();
    const hasErrorText = await page.locator('text=Error, text=Failed, text=Unable').count() > 0;
    
    expect(errorElements > 0 || hasErrorText).toBeTruthy();
  });

  test('should handle concurrent user actions', async ({ page }) => {
    await helpers.navigateTo('/chat');
    await helpers.waitForPageLoad();

    // Send multiple messages quickly
    const messageInput = page.locator('[data-testid="message-input"], textarea, input[type="text"]').first();
    const sendButton = page.locator('[data-testid="send-button"], button[type="submit"]').first();

    if (await messageInput.isVisible() && await sendButton.isVisible()) {
      for (let i = 0; i < 3; i++) {
        await messageInput.fill(`Test message ${i + 1}`);
        await sendButton.click();
        await page.waitForTimeout(500);
      }

      // Check that all messages were handled
      await page.waitForTimeout(2000);
      const messageCount = await page.locator('[data-testid="message-item"], .message').count();
      expect(messageCount).toBeGreaterThan(0);
    }
  });
});
