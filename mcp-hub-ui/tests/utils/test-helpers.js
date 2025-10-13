/**
 * Test helper utilities for MCP Hub UI tests
 */

import { expect } from '@playwright/test';

export class TestHelpers {
  constructor(page) {
    this.page = page;
  }

  /**
   * Wait for the page to be fully loaded
   */
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.page.waitForSelector('[data-testid="app-container"]', { timeout: 10000 });
  }

  /**
   * Navigate to a specific route
   */
  async navigateTo(route) {
    await this.page.goto(route);
    await this.waitForPageLoad();
  }

  /**
   * Wait for API response
   */
  async waitForApiResponse(url, timeout = 10000) {
    return await this.page.waitForResponse(response => 
      response.url().includes(url) && response.status() === 200,
      { timeout }
    );
  }

  /**
   * Check if element is visible
   */
  async isElementVisible(selector) {
    try {
      await this.page.waitForSelector(selector, { timeout: 5000 });
      return await this.page.isVisible(selector);
    } catch {
      return false;
    }
  }

  /**
   * Wait for loading to complete
   */
  async waitForLoadingComplete() {
    // Wait for loading indicators to disappear
    await this.page.waitForFunction(() => {
      const loadingElements = document.querySelectorAll('[data-testid="loading"]');
      return loadingElements.length === 0;
    }, { timeout: 15000 });
  }

  /**
   * Check for error messages
   */
  async checkForErrors() {
    const errorSelectors = [
      '[data-testid="error"]',
      '.error',
      '[role="alert"]',
      '.MuiAlert-root'
    ];

    for (const selector of errorSelectors) {
      const isVisible = await this.isElementVisible(selector);
      if (isVisible) {
        const errorText = await this.page.textContent(selector);
        throw new Error(`Error found: ${errorText}`);
      }
    }
  }

  /**
   * Take screenshot for debugging
   */
  async takeScreenshot(name) {
    await this.page.screenshot({ 
      path: `test-results/screenshots/${name}.png`,
      fullPage: true 
    });
  }

  /**
   * Mock API responses
   */
  async mockApiResponse(url, response) {
    await this.page.route(url, route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });
  }

  /**
   * Intercept and log API calls
   */
  async logApiCalls() {
    this.page.on('response', response => {
      console.log(`API Call: ${response.url()} - Status: ${response.status()}`);
    });
  }

  /**
   * Wait for specific text content
   */
  async waitForTextContent(selector, text, timeout = 10000) {
    await this.page.waitForFunction(
      ({ selector, text }) => {
        const element = document.querySelector(selector);
        return element && element.textContent.includes(text);
      },
      { selector, text },
      { timeout }
    );
  }

  /**
   * Fill form field safely
   */
  async fillField(selector, value) {
    await this.page.waitForSelector(selector);
    await this.page.fill(selector, value);
  }

  /**
   * Click button safely
   */
  async clickButton(selector) {
    await this.page.waitForSelector(selector);
    await this.page.click(selector);
  }

  /**
   * Wait for dialog to appear
   */
  async waitForDialog() {
    await this.page.waitForSelector('[role="dialog"]', { timeout: 5000 });
  }

  /**
   * Close dialog
   */
  async closeDialog() {
    const closeButton = this.page.locator('[data-testid="close-dialog"]');
    if (await closeButton.isVisible()) {
      await closeButton.click();
    }
  }

  /**
   * Check page title
   */
  async checkPageTitle(expectedTitle) {
    const title = await this.page.title();
    expect(title).toContain(expectedTitle);
  }

  /**
   * Check URL
   */
  async checkUrl(expectedPath) {
    const url = this.page.url();
    expect(url).toContain(expectedPath);
  }

  /**
   * Wait for network to be idle
   */
  async waitForNetworkIdle() {
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Get element text content
   */
  async getTextContent(selector) {
    await this.page.waitForSelector(selector);
    return await this.page.textContent(selector);
  }

  /**
   * Check if element exists
   */
  async elementExists(selector) {
    const count = await this.page.locator(selector).count();
    return count > 0;
  }

  /**
   * Wait for element to be enabled
   */
  async waitForElementEnabled(selector, timeout = 10000) {
    await this.page.waitForFunction(
      (selector) => {
        const element = document.querySelector(selector);
        return element && !element.disabled;
      },
      selector,
      { timeout }
    );
  }
}
