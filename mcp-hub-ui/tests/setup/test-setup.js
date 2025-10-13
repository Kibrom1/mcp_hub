/**
 * Test setup and configuration for MCP Hub UI tests
 */

import { test as base } from '@playwright/test';

// Extend base test with custom fixtures
export const test = base.extend({
  // Custom page with pre-configured settings
  page: async ({ page }, use) => {
    // Set default viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    
    // Enable request/response logging
    page.on('request', request => {
      console.log(`Request: ${request.method()} ${request.url()}`);
    });
    
    page.on('response', response => {
      console.log(`Response: ${response.status()} ${response.url()}`);
    });
    
    await use(page);
  },
});

// Global setup
export const globalSetup = async () => {
  console.log('Setting up MCP Hub UI tests...');
  
  // Check if backend is running
  try {
    const response = await fetch('http://localhost:8000/api/health');
    if (!response.ok) {
      throw new Error('Backend not running');
    }
    console.log('Backend is running and healthy');
  } catch (error) {
    console.warn('Backend not available:', error.message);
  }
  
  // Check if frontend is running
  try {
    const response = await fetch('http://localhost:3001');
    if (!response.ok) {
      throw new Error('Frontend not running');
    }
    console.log('Frontend is running');
  } catch (error) {
    console.warn('Frontend not available:', error.message);
  }
};

// Global teardown
export const globalTeardown = async () => {
  console.log('Cleaning up MCP Hub UI tests...');
};

// Test timeout configuration
export const timeout = 30000; // 30 seconds

// Retry configuration
export const retries = 2;

// Parallel execution
export const fullyParallel = true;

// Worker configuration
export const workers = process.env.CI ? 1 : undefined;
