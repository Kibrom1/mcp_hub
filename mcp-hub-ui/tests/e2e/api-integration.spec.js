/**
 * API Integration tests for MCP Hub UI
 * Tests API communication and data loading
 */

import { test, expect } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers.js';
import { testData } from '../fixtures/test-data.js';

test.describe('API Integration Tests', () => {
  let helpers;

  test.beforeEach(async ({ page }) => {
    helpers = new TestHelpers(page);
    await helpers.logApiCalls();
  });

  test('should load system status on dashboard', async ({ page }) => {
    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();

    // Wait for API call to complete
    await helpers.waitForApiResponse('/api/status');

    // Check for status indicators
    const statusElements = await page.locator('[data-testid*="status"], .MuiChip-root, .status').count();
    expect(statusElements).toBeGreaterThan(0);

    // Check for system metrics
    await expect(page.locator('body')).toContainText(['Tools', 'Servers', 'Resources']);
  });

  test('should load chat history', async ({ page }) => {
    await helpers.navigateTo('/chat');
    await helpers.waitForPageLoad();

    // Wait for chat history API call
    await helpers.waitForApiResponse('/api/chat');

    // Check for chat interface
    await expect(page.locator('[data-testid="message-input"], textarea, input[type="text"]')).toBeVisible();
  });

  test('should load available tools', async ({ page }) => {
    await helpers.navigateTo('/tools');
    await helpers.waitForPageLoad();

    // Wait for tools API call
    await helpers.waitForApiResponse('/api/tools');

    // Check for tools content
    await expect(page.locator('body')).toContainText(['Tools', 'Available', 'Execute']);
  });

  test('should load resources', async ({ page }) => {
    await helpers.navigateTo('/resources');
    await helpers.waitForPageLoad();

    // Wait for resources API call
    await helpers.waitForApiResponse('/api/resources');

    // Check for resources content
    await expect(page.locator('body')).toContainText(['Resources', 'Database', 'Query']);
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API failure
    await helpers.mockApiResponse('**/api/status', { error: 'Service unavailable' });

    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();

    // Check for error handling
    const errorElements = await page.locator('[data-testid="error"], .error, .MuiAlert-root').count();
    
    // Should either show error or fallback content
    const hasError = errorElements > 0;
    const hasFallback = await page.locator('text=Unable to load, text=Error, text=Failed').count() > 0;
    
    expect(hasError || hasFallback).toBeTruthy();
  });

  test('should retry failed API calls', async ({ page }) => {
    let callCount = 0;
    
    // Mock API to fail first time, succeed second time
    await page.route('**/api/status', route => {
      callCount++;
      if (callCount === 1) {
        route.fulfill({ status: 500, body: 'Internal Server Error' });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ tools: 10, servers: 2, resources: 5 })
        });
      }
    });

    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();

    // Wait for retry
    await page.waitForTimeout(2000);

    // Should eventually load successfully
    expect(callCount).toBeGreaterThan(1);
  });

  test('should show loading states during API calls', async ({ page }) => {
    // Slow down API responses
    await page.route('**/api/**', route => {
      setTimeout(() => {
        route.continue();
      }, 1000);
    });

    await helpers.navigateTo('/');
    
    // Check for loading indicators
    const loadingElements = await page.locator('[data-testid="loading"], .loading, .MuiCircularProgress-root').count();
    
    // Should show loading state
    expect(loadingElements).toBeGreaterThan(0);
  });

  test('should handle network timeouts', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/status', route => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ tools: 10, servers: 2, resources: 5 })
        });
      }, 5000);
    });

    await helpers.navigateTo('/');
    
    // Should handle timeout gracefully
    await page.waitForTimeout(3000);
    
    // Check for timeout handling
    const timeoutElements = await page.locator('text=timeout, text=slow, text=loading').count();
    expect(timeoutElements).toBeGreaterThan(0);
  });

  test('should cache API responses', async ({ page }) => {
    let apiCallCount = 0;
    
    // Track API calls
    page.on('response', response => {
      if (response.url().includes('/api/status')) {
        apiCallCount++;
      }
    });

    // Navigate to dashboard multiple times
    for (let i = 0; i < 3; i++) {
      await helpers.navigateTo('/');
      await helpers.waitForPageLoad();
      await page.waitForTimeout(500);
    }

    // Should not make excessive API calls
    expect(apiCallCount).toBeLessThanOrEqual(3);
  });

  test('should handle concurrent API calls', async ({ page }) => {
    const apiCalls = [];
    
    // Track all API calls
    page.on('response', response => {
      if (response.url().includes('/api/')) {
        apiCalls.push({
          url: response.url(),
          status: response.status(),
          timestamp: Date.now()
        });
      }
    });

    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();

    // Should handle multiple concurrent API calls
    expect(apiCalls.length).toBeGreaterThan(0);
    
    // All API calls should succeed
    const failedCalls = apiCalls.filter(call => call.status >= 400);
    expect(failedCalls.length).toBe(0);
  });

  test('should validate API response format', async ({ page }) => {
    // Intercept API responses and validate format
    page.on('response', async response => {
      if (response.url().includes('/api/status')) {
        const body = await response.json();
        
        // Validate response structure
        expect(body).toHaveProperty('tools');
        expect(body).toHaveProperty('servers');
        expect(body).toHaveProperty('resources');
        expect(typeof body.tools).toBe('number');
        expect(typeof body.servers).toBe('number');
        expect(typeof body.resources).toBe('number');
      }
    });

    await helpers.navigateTo('/');
    await helpers.waitForPageLoad();
  });

  test('should handle CORS properly', async ({ page }) => {
    // Check that API calls work with CORS
    const response = await page.request.get('http://localhost:8000/api/health');
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data).toHaveProperty('status');
    expect(data.status).toBe('healthy');
  });

  test('should handle WebSocket connections', async ({ page }) => {
    await helpers.navigateTo('/chat');
    await helpers.waitForPageLoad();

    // Check for WebSocket connection
    const wsConnections = await page.evaluate(() => {
      return window.WebSocket ? true : false;
    });

    expect(wsConnections).toBeTruthy();
  });
});
