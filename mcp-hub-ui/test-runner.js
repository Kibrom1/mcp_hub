// Simple test runner using Playwright
const { chromium } = require('playwright');

async function runTests() {
  console.log('🚀 Starting MCP Hub UI Tests...');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Test 1: Load homepage
    console.log('📄 Testing homepage load...');
    await page.goto('http://localhost:3001');
    const title = await page.title();
    console.log(`✅ Homepage loaded with title: ${title}`);
    
    // Test 2: Check for navigation elements
    console.log('🧭 Testing navigation...');
    const navLinks = await page.locator('nav a, [role="navigation"] a').count();
    console.log(`✅ Found ${navLinks} navigation links`);
    
    // Test 3: Navigate to chat page
    console.log('💬 Testing chat page navigation...');
    await page.click('a[href="/chat"]');
    await page.waitForTimeout(1000);
    const chatUrl = page.url();
    console.log(`✅ Navigated to chat: ${chatUrl}`);
    
    // Test 4: Navigate to tools page
    console.log('🔧 Testing tools page navigation...');
    await page.click('a[href="/tools"]');
    await page.waitForTimeout(1000);
    const toolsUrl = page.url();
    console.log(`✅ Navigated to tools: ${toolsUrl}`);
    
    // Test 5: Navigate to resources page
    console.log('📊 Testing resources page navigation...');
    await page.click('a[href="/resources"]');
    await page.waitForTimeout(1000);
    const resourcesUrl = page.url();
    console.log(`✅ Navigated to resources: ${resourcesUrl}`);
    
    // Test 6: Navigate to settings page
    console.log('⚙️ Testing settings page navigation...');
    await page.click('a[href="/settings"]');
    await page.waitForTimeout(1000);
    const settingsUrl = page.url();
    console.log(`✅ Navigated to settings: ${settingsUrl}`);
    
    console.log('🎉 All tests passed!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

runTests().catch(console.error);
