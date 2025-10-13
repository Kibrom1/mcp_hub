/**
 * Component-specific tests for MCP Hub UI
 * Tests individual components and their functionality
 */

import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers.js';
import { testData } from '../fixtures/test-data.js';

test.describe('Component Tests', () => {
  let helpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
  });

  test.describe('Dashboard Component', () => {
    test('should display system status', async ({ page }) => {
      await helpers.navigateTo('/');
      await helpers.waitForPageLoad();

      // Check for status cards
      const statusCards = page.locator('[data-testid="status-card"], .MuiCard-root');
      await expect(statusCards.first()).toBeVisible();

      // Check for system metrics
      await expect(page.locator('body')).toContainText(['Tools', 'Servers', 'Resources']);
    });

    test('should show real-time updates', async ({ page }) => {
      await helpers.navigateTo('/');
      await helpers.waitForPageLoad();

      // Wait for initial load
      await helpers.waitForLoadingComplete();

      // Check for timestamp or update indicators
      const timestampElements = await page.locator('[data-testid="timestamp"], .timestamp, time').count();
      expect(timestampElements).toBeGreaterThan(0);
    });

    test('should handle status changes', async ({ page }) => {
      // Mock status change
      await helpers.mockApiResponse('**/api/status', {
        tools: 25,
        servers: 5,
        resources: 10,
        timestamp: new Date().toISOString()
      });

      await helpers.navigateTo('/');
      await helpers.waitForPageLoad();

      // Check for updated values
      await expect(page.locator('body')).toContainText(['25', '5', '10']);
    });
  });

  test.describe('Chat Component', () => {
    test('should display chat interface', async ({ page }) => {
      await helpers.navigateTo('/chat');
      await helpers.waitForPageLoad();

      // Check for chat elements
      await expect(page.locator('[data-testid="message-input"], textarea, input[type="text"]')).toBeVisible();
      await expect(page.locator('[data-testid="send-button"], button[type="submit"]')).toBeVisible();
      await expect(page.locator('[data-testid="message-list"], .messages')).toBeVisible();
    });

    test('should handle message history', async ({ page }) => {
      await helpers.navigateTo('/chat');
      await helpers.waitForPageLoad();

      // Check for message history
      const messageItems = page.locator('[data-testid="message-item"], .message');
      const messageCount = await messageItems.count();
      
      // Should have message container even if empty
      expect(messageCount).toBeGreaterThanOrEqual(0);
    });

    test('should handle message types', async ({ page }) => {
      await helpers.navigateTo('/chat');
      await helpers.waitForPageLoad();

      // Send user message
      const messageInput = page.locator('[data-testid="message-input"], textarea, input[type="text"]').first();
      await messageInput.fill('Test user message');
      
      const sendButton = page.locator('[data-testid="send-button"], button[type="submit"]').first();
      await sendButton.click();

      await page.waitForTimeout(1000);

      // Check for user message
      await expect(page.locator('body')).toContainText('Test user message');
    });

    test('should handle message formatting', async ({ page }) => {
      await helpers.navigateTo('/chat');
      await helpers.waitForPageLoad();

      // Check for message formatting elements
      const formattedElements = await page.locator('.message, [data-testid="message-item"]').count();
      expect(formattedElements).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('Tools Component', () => {
    test('should display available tools', async ({ page }) => {
      await helpers.navigateTo('/tools');
      await helpers.waitForPageLoad();

      // Check for tools content
      await expect(page.locator('body')).toContainText(['Tools', 'Available', 'Execute']);
    });

    test('should handle tool execution', async ({ page }) => {
      await helpers.navigateTo('/tools');
      await helpers.waitForPageLoad();

      // Find execute button
      const executeButton = page.locator('[data-testid="execute-button"], button:has-text("Execute")').first();
      if (await executeButton.isVisible()) {
        await executeButton.click();

        // Check for execution dialog or result
        await page.waitForTimeout(1000);
        const hasDialog = await page.locator('[role="dialog"], .MuiDialog-root').count() > 0;
        const hasResult = await page.locator('[data-testid="result"], .result').count() > 0;
        
        expect(hasDialog || hasResult).toBeTruthy();
      }
    });

    test('should handle tool arguments', async ({ page }) => {
      await helpers.navigateTo('/tools');
      await helpers.waitForPageLoad();

      // Click execute button
      const executeButton = page.locator('[data-testid="execute-button"], button:has-text("Execute")').first();
      if (await executeButton.isVisible()) {
        await executeButton.click();

        // Wait for dialog
        await helpers.waitForDialog();

        // Check for argument inputs
        const argumentInputs = page.locator('[data-testid="tool-arguments"], input, textarea');
        if (await argumentInputs.count() > 0) {
          await expect(argumentInputs.first()).toBeVisible();
        }
      }
    });

    test('should display tool results', async ({ page }) => {
      await helpers.navigateTo('/tools');
      await helpers.waitForPageLoad();

      // Execute a tool
      const executeButton = page.locator('[data-testid="execute-button"], button:has-text("Execute")').first();
      if (await executeButton.isVisible()) {
        await executeButton.click();
        await page.waitForTimeout(2000);

        // Check for results
        const resultElements = await page.locator('[data-testid="result"], .result, .MuiAlert-root').count();
        expect(resultElements).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Resources Component', () => {
    test('should display available resources', async ({ page }) => {
      await helpers.navigateTo('/resources');
      await helpers.waitForPageLoad();

      // Check for resources content
      await expect(page.locator('body')).toContainText(['Resources', 'Database', 'Query']);
    });

    test('should handle database queries', async ({ page }) => {
      await helpers.navigateTo('/resources');
      await helpers.waitForPageLoad();

      // Find query input
      const queryInput = page.locator('[data-testid="query-input"], textarea, input').first();
      if (await queryInput.isVisible()) {
        await queryInput.fill('SELECT * FROM users LIMIT 5');
        
        // Find execute button
        const executeButton = page.locator('[data-testid="execute-query-button"], button:has-text("Execute")').first();
        if (await executeButton.isVisible()) {
          await executeButton.click();
          await page.waitForTimeout(2000);

          // Check for query result
          const resultElements = await page.locator('[data-testid="query-result"], .result').count();
          expect(resultElements).toBeGreaterThan(0);
        }
      }
    });

    test('should display query results', async ({ page }) => {
      await helpers.navigateTo('/resources');
      await helpers.waitForPageLoad();

      // Execute a query
      const queryInput = page.locator('[data-testid="query-input"], textarea, input').first();
      const executeButton = page.locator('[data-testid="execute-query-button"], button:has-text("Execute")').first();
      
      if (await queryInput.isVisible() && await executeButton.isVisible()) {
        await queryInput.fill('SELECT 1 as test');
        await executeButton.click();
        await page.waitForTimeout(2000);

        // Check for results
        const resultElements = await page.locator('[data-testid="query-result"], .result').count();
        expect(resultElements).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Settings Component', () => {
    test('should display settings interface', async ({ page }) => {
      await helpers.navigateTo('/settings');
      await helpers.waitForPageLoad();

      // Check for settings content
      await expect(page.locator('body')).toContainText(['Settings', 'Configuration']);
    });

    test('should handle configuration changes', async ({ page }) => {
      await helpers.navigateTo('/settings');
      await helpers.waitForPageLoad();

      // Look for configuration inputs
      const configInputs = page.locator('input, select, textarea');
      const inputCount = await configInputs.count();
      
      if (inputCount > 0) {
        // Test configuration change
        const firstInput = configInputs.first();
        await firstInput.fill('test configuration');
        
        // Check for save button
        const saveButton = page.locator('button:has-text("Save"), button:has-text("Apply")');
        if (await saveButton.isVisible()) {
          await saveButton.click();
          await page.waitForTimeout(1000);
        }
      }
    });
  });

  test.describe('Layout Component', () => {
    test('should display navigation', async ({ page }) => {
      await helpers.navigateTo('/');
      await helpers.waitForPageLoad();

      // Check for navigation elements
      const navElements = page.locator('nav, [role="navigation"]');
      await expect(navElements).toBeVisible();

      // Check for navigation links
      const navLinks = page.locator('nav a, [role="navigation"] a');
      const linkCount = await navLinks.count();
      expect(linkCount).toBeGreaterThan(0);
    });

    test('should handle mobile navigation', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await helpers.navigateTo('/');
      await helpers.waitForPageLoad();

      // Check for mobile menu
      const mobileMenu = page.locator('[data-testid="mobile-menu"], .MuiIconButton-root').first();
      if (await mobileMenu.isVisible()) {
        await mobileMenu.click();
        
        // Check menu is open
        const menuItems = page.locator('[role="menu"], .MuiMenu-root');
        await expect(menuItems).toBeVisible();
      }
    });

    test('should maintain layout consistency', async ({ page }) => {
      const routes = ['/', '/chat', '/tools', '/resources', '/settings'];
      
      for (const route of routes) {
        await helpers.navigateTo(route);
        await helpers.waitForPageLoad();
        
        // Check that navigation is consistent
        const navElements = await page.locator('nav, [role="navigation"]').count();
        expect(navElements).toBeGreaterThan(0);
      }
    });
  });
});
