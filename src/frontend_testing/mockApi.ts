/**
 * Mock API Service
 * 
 * Provides mocked implementations of API functions for testing purposes.
 * These mocks simulate network delays and return predictable responses,
 * allowing tests to run without requiring a backend server.
 * 
 * All functions maintain the same interface as the real API functions
 * but return mock data instead of making actual HTTP requests.
 */

// Type definitions for API responses
import type {
  ChatResponse,
  WebsiteListResponse,
  WebsiteChunksResponse,
  ApiError,
} from '../types';

/**
 * Simulate network delay
 * 
 * Adds a delay to simulate network latency in API calls.
 * This makes the mock responses feel more realistic.
 * 
 * @param ms - Milliseconds to delay (default: 500-1500ms random)
 * @returns Promise that resolves after the delay
 */
const delay = (ms: number = Math.random() * 1000 + 500): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Mock sendChatMessage function
 * 
 * Simulates sending a chat message and receiving an AI response.
 * Returns a mock response with a generated conversation ID and AI response.
 * 
 * @param message - The user's message text
 * @param conversationId - Optional conversation ID (generates new one if not provided)
 * @returns Promise resolving to ChatResponse with mock AI response
 */
export async function mockSendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  // Simulate network delay
  await delay();
  
  // Generate or use provided conversation ID
  const convId = conversationId || `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  // Generate mock AI response based on user message
  const mockResponses: Record<string, string> = {
    'hello': 'Hello! How can I assist you today?',
    'help': 'I\'m here to help! What do you need assistance with?',
    'account': 'I can help you with account-related questions. What specifically would you like to know?',
    'password': 'I can help you reset your password. Please provide your email address.',
    'billing': 'For billing inquiries, I can help you understand your charges or update payment methods.',
  };
  
  // Find a matching response or generate a generic one
  const lowerMessage = message.toLowerCase();
  let response = 'Thank you for your message. I\'m here to help you with any questions or issues you might have.';
  
  for (const [key, value] of Object.entries(mockResponses)) {
    if (lowerMessage.includes(key)) {
      response = value;
      break;
    }
  }
  
  // If no match, create a contextual response
  if (response === 'Thank you for your message. I\'m here to help you with any questions or issues you might have.') {
    response = `I understand you're asking about "${message}". Let me help you with that. Could you provide more details?`;
  }
  
  return {
    response,
    conversation_id: convId,
  };
}

/**
 * Mock getWebsites function
 * 
 * Simulates retrieving a list of all scraped websites.
 * Returns a mock list of websites.
 * 
 * @returns Promise resolving to WebsiteListResponse with mock websites
 */
export async function mockGetWebsites(): Promise<WebsiteListResponse> {
  // Simulate network delay
  await delay();
  
  // Return mock list of websites
  return {
    websites: [
      {
        id: 1,
        url: 'https://example.com',
        title: 'Example Website',
        status: 'completed',
        scraped_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
      },
      {
        id: 2,
        url: 'https://test.com',
        title: 'Test Website',
        status: 'completed',
        scraped_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
      },
      {
        id: 3,
        url: 'https://demo.com',
        title: 'Demo Website',
        status: 'pending',
        scraped_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      },
    ],
  };
}

/**
 * Mock getWebsite function
 * 
 * Simulates retrieving a website and its chunks by ID.
 * Returns mock website data with content chunks.
 * 
 * @param id - The ID of the website to retrieve
 * @returns Promise resolving to WebsiteChunksResponse with mock data
 */
export async function mockGetWebsite(id: number): Promise<WebsiteChunksResponse> {
  // Simulate network delay
  await delay();
  
  // Return mock website with chunks
  return {
    website: {
      id,
      url: `https://example${id}.com`,
      title: `Example Website ${id}`,
      status: 'completed',
      scraped_at: new Date(Date.now() - 86400000).toISOString(),
    },
    chunks: [
      {
        id: id * 10 + 1,
        website_id: id,
        chunk_text: `This is chunk 1 for website ${id}. It contains important information about the website's content and features.`,
        chunk_index: 0,
        metadata: { section: 'introduction' },
        created_at: new Date().toISOString(),
      },
      {
        id: id * 10 + 2,
        website_id: id,
        chunk_text: `This is chunk 2 for website ${id}. It provides additional details about the services and offerings.`,
        chunk_index: 1,
        metadata: { section: 'services' },
        created_at: new Date().toISOString(),
      },
      {
        id: id * 10 + 3,
        website_id: id,
        chunk_text: `This is chunk 3 for website ${id}. It includes contact information and support details.`,
        chunk_index: 2,
        metadata: { section: 'contact' },
        created_at: new Date().toISOString(),
      },
    ],
  };
}

/**
 * Mock getWebsiteByTitle function
 * 
 * Simulates retrieving a website and its chunks by title.
 * Returns mock website data with content chunks.
 * 
 * @param title - The title of the website to retrieve
 * @returns Promise resolving to WebsiteChunksResponse with mock data
 */
export async function mockGetWebsiteByTitle(title: string): Promise<WebsiteChunksResponse> {
  // Simulate network delay
  await delay();
  
  // Return mock website with chunks based on title
  const websiteId = title.length; // Use title length as mock ID
  
  return {
    website: {
      id: websiteId,
      url: `https://${title.toLowerCase().replace(/\s+/g, '')}.com`,
      title,
      status: 'completed',
      scraped_at: new Date(Date.now() - 86400000).toISOString(),
    },
    chunks: [
      {
        id: websiteId * 10 + 1,
        website_id: websiteId,
        chunk_text: `Content chunk 1 for "${title}". This contains the main information about the website.`,
        chunk_index: 0,
        metadata: { section: 'main' },
        created_at: new Date().toISOString(),
      },
      {
        id: websiteId * 10 + 2,
        website_id: websiteId,
        chunk_text: `Content chunk 2 for "${title}". Additional details and features are described here.`,
        chunk_index: 1,
        metadata: { section: 'features' },
        created_at: new Date().toISOString(),
      },
    ],
  };
}

/**
 * Mock getWebsiteByUrl function
 * 
 * Simulates retrieving a website and its chunks by URL.
 * Returns mock website data with content chunks.
 * 
 * @param url - The URL of the website to retrieve
 * @returns Promise resolving to WebsiteChunksResponse with mock data
 */
export async function mockGetWebsiteByUrl(url: string): Promise<WebsiteChunksResponse> {
  // Simulate network delay
  await delay();
  
  // Extract domain from URL for mock data
  const domain = url.replace(/^https?:\/\//, '').replace(/\/.*$/, '');
  const websiteId = domain.length; // Use domain length as mock ID
  
  return {
    website: {
      id: websiteId,
      url,
      title: `${domain.charAt(0).toUpperCase() + domain.slice(1)} Website`,
      status: 'completed',
      scraped_at: new Date(Date.now() - 86400000).toISOString(),
    },
    chunks: [
      {
        id: websiteId * 10 + 1,
        website_id: websiteId,
        chunk_text: `Content from ${url}. This is the first chunk containing main content.`,
        chunk_index: 0,
        metadata: { source: url },
        created_at: new Date().toISOString(),
      },
      {
        id: websiteId * 10 + 2,
        website_id: websiteId,
        chunk_text: `Additional content from ${url}. This chunk contains supplementary information.`,
        chunk_index: 1,
        metadata: { source: url },
        created_at: new Date().toISOString(),
      },
    ],
  };
}

/**
 * Mock healthCheck function
 * 
 * Simulates a health check request to the backend.
 * Always returns a healthy status.
 * 
 * @returns Promise resolving to health status object
 */
export async function mockHealthCheck(): Promise<{ status: string }> {
  // Simulate network delay (shorter for health check)
  await delay(200);
  
  // Always return healthy status
  return {
    status: 'healthy',
  };
}

/**
 * Mock error generator
 * 
 * Simulates API errors for testing error handling.
 * Can be used to test error states in components.
 * 
 * @param message - Error message to return
 * @param status - HTTP status code (default: 500)
 * @returns Promise that rejects with ApiError
 */
export async function mockApiError(
  message: string = 'Mock API Error',
  status: number = 500
): Promise<never> {
  // Simulate network delay before error
  await delay(300);
  
  // Throw mock error
  const error: ApiError = {
    error: message,
    message,
    status,
  };
  
  throw error;
}
