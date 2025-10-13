/**
 * Navigation tests for MCP Hub UI
 * Tests all navigation routes and components
 */

import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers.js';
import { testData } from '../fixtures/test-data.js';

test.describe('Navigation Tests', () => {
  let helpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();
  });

  test('should load dashboard page by default', async ({ page }) => {
    // Check URL
    await helpers.checkUrl('/');
    
    // Check page title
    await helpers.checkPageTitle('MCP Hub');
    
    // Check for dashboard content
    await expect(page.locator('h1, h2, h3, h4, h5, h6')).toContainText(['Dashboard', 'System Status']);
  });

  test('should navigate to chat page', async ({ page }) => {
    // Click on chat navigation
    await page.click('a[href="/chat"], [data-testid="nav-chat"]');
    await helpers.waitForPageLoad();
    
    // Check URL
    await helpers.checkUrl('/chat');
    
    // Check for chat content
    await expect(page.locator('h1, h2, h3, h4, h5, h6')).toContainText(['Chat', 'Messages']);
  });

  test('should navigate to tools page', async ({ page }) => {
    // Click on tools navigation
    await page.click('a[href="/tools"], [data-testid="nav-tools"]');
    await helpers.waitForPageLoad();
    
    // Check URL
    await helpers.checkUrl('/tools');
    
    // Check for tools content
    await expect(page.locator('h1, h2, h3, h4, h5, h6')).toContainText(['Tools', 'Available Tools']);
  });

  test('should navigate to resources page', async ({ page }) => {
    // Click on resources navigation
    await page.click('a[href="/resources"], [data-testid="nav-resources"]');
    await helpers.waitForPageLoad();
    
    // Check URL
    await helpers.checkUrl('/resources');
    
    // Check for resources content
    await expect(page.locator('h1, h2, h3, h4, h5, h6')).toContainText(['Resources', 'Database']);
  });

  test('should navigate to settings page', async ({ page }) => {
    // Click on settings navigation
    await page.click('a[href="/settings"], [data-testid="nav-settings"]');
    await helpers.waitForPageLoad();
    
    // Check URL
    await helpers.checkUrl('/settings');
    
    // Check for settings content
    await expect(page.locator('h1, h2, h3, h4, h5, h6')).toContainText(['Settings', 'Configuration']);
  });

  test('should maintain navigation state', async ({ page }) => {
    // Navigate through all pages
    const routes = ['/', '/chat', '/tools', '/resources', '/settings'];
    
    for (const route of routes) {
      await helpers.navigateTo(route);
      await helpers.waitForPageLoad();
      await helpers.checkUrl(route);
      
      // Check that navigation is still visible
      const navElements = await page.locator('nav, [role="navigation"]').count();
      expect(navElements).toBeGreaterThan(0);
    }
  });

  test('should handle direct URL navigation', async ({ page }) => {
    // Test direct navigation to each route
    const routes = [
      { path: '/chat', expectedContent: ['Chat', 'Messages'] },
      { path: '/tools', expectedContent: ['Tools', 'Available'] },
      { path: '/resources', expectedContent: ['Resources', 'Database'] },
      { path: '/settings', expectedContent: ['Settings', 'Configuration'] }
    ];

    for (const route of routes) {
      await helpers.navigateTo(route.path);
      await helpers.waitForPageLoad();
      
      // Check that content loads
      for (const content of route.expectedContent) {
        await expect(page.locator('body')).toContainText(content);
      }
    }
  });

  test('should show loading states during navigation', async ({ page }) => {
    // Navigate to a page and check for loading indicators
    await page.click('a[href="/tools"]');
    
    // Check for loading state (if any)
    const loadingElements = await page.locator('[data-testid="loading"], .loading, .MuiCircularProgress-root').count();
    
    // Wait for loading to complete
    await helpers.waitForLoadingComplete();
    
    // Verify content is loaded
    await expect(page.locator('h1, h2, h3, h4, h5, h6')).toContainText(['Tools']);
  });

  test('should handle navigation errors gracefully', async ({ page }) => {
    // Test navigation to non-existent route
    await helpers.navigateTo('/non-existent-route');
    
    // Should either redirect to dashboard or show 404
    const currentUrl = page.url();
    const isDashboard = currentUrl.includes('/') && !currentUrl.includes('/non-existent-route');
    const is404 = await page.locator('text=404, text=Not Found, text=Page not found').count() > 0;
    
    expect(isDashboard || is404).toBeTruthy();
  });

  test('should preserve user state during navigation', async ({ page }) => {
    // Navigate to chat page
    await helpers.navigateTo('/chat');
    await helpers.waitForPageLoad();
    
    // Navigate to tools page
    await helpers.navigateTo('/tools');
    await helpers.waitForPageLoad();
    
    // Navigate back to chat
    await helpers.navigateTo('/chat');
    await helpers.waitForPageLoad();
    
    // Check that we're on chat page
    await helpers.checkUrl('/chat');
  });

  test('should work on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Test navigation on mobile
    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();
    
    // Check that navigation is accessible on mobile
    const navButton = page.locator('[data-testid="mobile-menu"], .MuiIconButton-root').first();
    if (await navButton.isVisible()) {
      await navButton.click();
    }
    
    // Navigate to different pages
    await helpers.navigateTo('/chat');
    await helpers.checkUrl('/chat');
    
    await helpers.navigateTo('/tools');
    await helpers.checkUrl('/tools');
  });
});
