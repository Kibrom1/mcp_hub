# MCP Hub UI - E2E Tests

This directory contains comprehensive end-to-end tests for the MCP Hub UI using Playwright.

## Test Structure

```
tests/
├── e2e/                    # End-to-end test files
│   ├── navigation.spec.js  # Navigation and routing tests
│   ├── api-integration.spec.js  # API communication tests
│   ├── user-interactions.spec.js  # User interaction tests
│   └── components.spec.js  # Component-specific tests
├── fixtures/               # Test data and fixtures
│   └── test-data.js       # Test data and selectors
├── utils/                  # Test utilities and helpers
│   └── test-helpers.js    # Helper functions for tests
└── setup/                 # Test setup and configuration
    └── test-setup.js      # Global test configuration
```

## Running Tests

### Prerequisites

1. **Backend Running**: Ensure the MCP Hub backend is running on `http://localhost:8000`
2. **Frontend Running**: Ensure the React frontend is running on `http://localhost:3001`
3. **Dependencies Installed**: Run `npm install` in the `mcp-hub-ui` directory

### Test Commands

```bash
# Install Playwright browsers
npm run test:e2e:install

# Run all tests
npm run test:e2e

# Run tests with UI (interactive mode)
npm run test:e2e:ui

# Run tests in headed mode (visible browser)
npm run test:e2e:headed

# Run tests in debug mode
npm run test:e2e:debug

# Show test report
npm run test:e2e:report
```

### Running Specific Tests

```bash
# Run only navigation tests
npx playwright test tests/e2e/navigation.spec.js

# Run only API integration tests
npx playwright test tests/e2e/api-integration.spec.js

# Run tests for specific browser
npx playwright test --project=chromium

# Run tests in specific mode
npx playwright test --headed --project=chromium
```

## Test Categories

### 1. Navigation Tests (`navigation.spec.js`)
- ✅ Route navigation (Dashboard, Chat, Tools, Resources, Settings)
- ✅ Direct URL access
- ✅ Navigation state preservation
- ✅ Mobile navigation
- ✅ Error handling for invalid routes

### 2. API Integration Tests (`api-integration.spec.js`)
- ✅ Backend API health checks
- ✅ Data loading from APIs
- ✅ Error handling for API failures
- ✅ Loading states during API calls
- ✅ Network timeout handling
- ✅ API response validation

### 3. User Interaction Tests (`user-interactions.spec.js`)
- ✅ Chat message sending
- ✅ Tool execution with arguments
- ✅ Database query execution
- ✅ Form validation
- ✅ Button state handling
- ✅ Dialog interactions
- ✅ Keyboard navigation
- ✅ Copy functionality
- ✅ Responsive design interactions

### 4. Component Tests (`components.spec.js`)
- ✅ Dashboard component functionality
- ✅ Chat component features
- ✅ Tools component operations
- ✅ Resources component queries
- ✅ Settings component configuration
- ✅ Layout component navigation

## Test Configuration

### Playwright Configuration (`playwright.config.js`)
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari
- **Parallel Execution**: Enabled for faster test runs
- **Retries**: 2 retries on failure
- **Screenshots**: On failure
- **Videos**: On failure
- **Traces**: On first retry

### Test Data (`test-data.js`)
- API endpoints and expected responses
- Test user data and scenarios
- UI selectors and expected content
- Test scenarios and validation data

### Test Helpers (`test-helpers.js`)
- Page navigation utilities
- API response waiting
- Element visibility checks
- Error handling
- Screenshot capture
- Form interaction helpers

## CI/CD Integration

### GitHub Actions Workflow (`.github/workflows/e2e-tests.yml`)
- **Triggers**: Push to main/develop, Pull requests, Daily schedule
- **Environment**: Ubuntu latest with Node.js 18
- **Services**: Backend and Frontend startup
- **Artifacts**: Test reports and screenshots
- **Timeout**: 60 minutes

### Test Reports
- **HTML Report**: Interactive test results
- **JSON Report**: Machine-readable results
- **JUnit Report**: CI integration
- **Screenshots**: Failure screenshots
- **Videos**: Failure recordings
- **Traces**: Detailed execution traces

## Best Practices

### Test Writing
1. **Use data-testid attributes** for reliable element selection
2. **Wait for elements** before interacting with them
3. **Handle async operations** properly
4. **Use page object pattern** for complex interactions
5. **Mock external dependencies** when necessary

### Test Maintenance
1. **Keep tests independent** - no test should depend on another
2. **Clean up after tests** - reset state between tests
3. **Use meaningful test names** - describe what the test does
4. **Group related tests** - use describe blocks effectively
5. **Handle flaky tests** - add appropriate waits and retries

### Performance
1. **Run tests in parallel** when possible
2. **Use headless mode** for CI/CD
3. **Optimize test data** - use minimal required data
4. **Clean up resources** - close pages and contexts
5. **Monitor test duration** - optimize slow tests

## Troubleshooting

### Common Issues

1. **Tests failing due to timing**
   - Add appropriate waits
   - Use `waitForSelector` instead of `setTimeout`
   - Check for loading states

2. **Element not found**
   - Verify selectors are correct
   - Check if element is visible
   - Wait for element to appear

3. **API calls failing**
   - Ensure backend is running
   - Check API endpoints are correct
   - Verify CORS configuration

4. **Tests flaky**
   - Add retries
   - Improve element selection
   - Handle async operations properly

### Debug Mode
```bash
# Run tests in debug mode
npm run test:e2e:debug

# Run specific test in debug mode
npx playwright test tests/e2e/navigation.spec.js --debug
```

### Test Reports
```bash
# Generate and view test report
npm run test:e2e:report
```

## Contributing

When adding new tests:

1. **Follow naming conventions** - use descriptive test names
2. **Add appropriate test data** - update fixtures as needed
3. **Use helper functions** - leverage existing utilities
4. **Handle edge cases** - test error scenarios
5. **Document new features** - update this README

## Support

For issues with tests:
1. Check the test reports for detailed error information
2. Review the test logs for API call details
3. Verify that both backend and frontend are running
4. Check browser console for JavaScript errors
5. Review the test configuration for any issues
