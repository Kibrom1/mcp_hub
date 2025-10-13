/**
 * Test data and fixtures for MCP Hub UI tests
 */

export const testData = {
  // API endpoints
  api: {
    baseUrl: 'http://localhost:8000',
    endpoints: {
      health: '/api/health',
      status: '/api/status',
      chat: '/api/chat',
      tools: '/api/tools',
      resources: '/api/resources',
    }
  },

  // Test user data
  user: {
    testMessage: 'Hello, this is a test message for the chat functionality.',
    sqlQuery: 'SELECT * FROM users LIMIT 5;',
    toolName: 'read_file',
    toolArguments: {
      path: '/tmp/test.txt',
      content: 'This is a test file content.'
    }
  },

  // Expected UI elements
  selectors: {
    // Navigation
    navigation: {
      dashboard: '[data-testid="nav-dashboard"]',
      chat: '[data-testid="nav-chat"]',
      tools: '[data-testid="nav-tools"]',
      resources: '[data-testid="nav-resources"]',
      settings: '[data-testid="nav-settings"]',
    },

    // Dashboard
    dashboard: {
      statusCard: '[data-testid="status-card"]',
      toolsCount: '[data-testid="tools-count"]',
      serversCount: '[data-testid="servers-count"]',
      resourcesCount: '[data-testid="resources-count"]',
    },

    // Chat
    chat: {
      messageInput: '[data-testid="message-input"]',
      sendButton: '[data-testid="send-button"]',
      messageList: '[data-testid="message-list"]',
      messageItem: '[data-testid="message-item"]',
    },

    // Tools
    tools: {
      toolCard: '[data-testid="tool-card"]',
      executeButton: '[data-testid="execute-button"]',
      toolDialog: '[data-testid="tool-dialog"]',
      toolArguments: '[data-testid="tool-arguments"]',
    },

    // Resources
    resources: {
      resourceCard: '[data-testid="resource-card"]',
      queryInput: '[data-testid="query-input"]',
      executeQueryButton: '[data-testid="execute-query-button"]',
      queryResult: '[data-testid="query-result"]',
    },

    // Common
    loading: '[data-testid="loading"]',
    error: '[data-testid="error"]',
    success: '[data-testid="success"]',
  },

  // Test scenarios
  scenarios: {
    navigation: 'Test navigation between different pages',
    chatInteraction: 'Test chat functionality',
    toolExecution: 'Test tool execution',
    resourceQuery: 'Test resource querying',
    apiIntegration: 'Test API integration',
  }
};

export const expectedContent = {
  // Page titles
  titles: {
    dashboard: 'Dashboard',
    chat: 'Chat',
    tools: 'Tools',
    resources: 'Resources',
    settings: 'Settings',
  },

  // Expected API responses
  api: {
    health: {
      status: 'healthy',
      services: ['llm_manager', 'mcp_executor', 'database']
    },
    status: {
      tools: expect.any(Number),
      servers: expect.any(Number),
      resources: expect.any(Number),
    }
  }
};
