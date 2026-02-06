// Axios library for making HTTP requests to the backend API
import axios, { AxiosInstance, AxiosError } from 'axios';
// TypeScript type definitions for API responses and errors
import type { ChatResponse, ScrapeResponse, WebsiteListResponse, WebsiteChunksResponse, ApiError } from '@/types';

// Get API URL from environment variable
// Falls back to localhost:5000 if NEXT_PUBLIC_API_URL is not set
// This allows configuration via .env.local file
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Create axios instance with base configuration
// This instance is reused for all API calls to maintain consistent configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Error handling utility function
 * 
 * Converts various error types (Axios errors, generic errors) into a standardized ApiError format.
 * This ensures consistent error handling across all API calls.
 * 
 * @param error - The error object to process (can be AxiosError, Error, or unknown)
 * @returns ApiError object with standardized error information
 */
export function handleApiError(error: unknown): ApiError {
  // Check if error is an Axios error (HTTP request errors)
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    
    // Extract error message from response data if available
    // Backend may return error details in response.data.message
    const responseData = axiosError.response?.data;
    const errorMessage = 
      (responseData && typeof responseData === 'object' && 'message' in responseData)
        ? (responseData as { message: string }).message
        : axiosError.message;
    
    // Return standardized error object with Axios error details
    return {
      error: axiosError.message,
      message: errorMessage,
      status: axiosError.response?.status,
    };
  }
  
  // Handle non-Axios errors (network errors, unexpected errors)
  return {
    error: 'An unexpected error occurred',
    message: error instanceof Error ? error.message : 'Unknown error',
  };
}

/**
 * Send a chat message to the backend and receive an AI response
 * 
 * Sends a user message to the chat endpoint, which processes the message,
 * retrieves relevant context from the database, and generates an AI response.
 * 
 * @param message - The user's message text
 * @param conversationId - Optional conversation ID to continue an existing conversation
 * @returns Promise resolving to ChatResponse containing AI response and conversation ID
 * @throws ApiError if the request fails
 */
export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  try {
    // Send POST request to chat endpoint with message and optional conversation ID
    const response = await apiClient.post<ChatResponse>('/api/chat/message', {
      message,
      conversation_id: conversationId,
    });
    // Return the response data (contains AI response and conversation ID)
    return response.data;
  } catch (error) {
    // Convert error to standardized ApiError format
    throw handleApiError(error);
  }
}

// /**
//  * Scrape a website and store its content in the database
//  * 
//  * Sends a website URL to the scraping endpoint, which uses Firecrawl API
//  * to scrape the website, chunk the content, generate embeddings, and store
//  * everything in the database.
//  * 
//  * @param url - The URL of the website to scrape
//  * @returns Promise resolving to ScrapeResponse containing website ID and status
//  * @throws ApiError if the request fails
//  */
// export async function scrapeWebsite(url: string): Promise<ScrapeResponse> {
//   try {
//     // Send POST request to scraping endpoint with website URL
//     const response = await apiClient.post<ScrapeResponse>('/api/websites/scrape', {
//       url,
//     });
//     // Return the response data (contains website ID and status)
//     return response.data;
//   } catch (error) {
//     // Convert error to standardized ApiError format
//     throw handleApiError(error);
//   }
// }

/**
 * Get a list of all scraped websites
 * 
 * Retrieves a list of all websites that have been scraped and stored in the database.
 * Note: This endpoint may not be implemented in the backend yet.
 * 
 * @returns Promise resolving to WebsiteListResponse containing array of websites
 * @throws ApiError if the request fails
 */
export async function getWebsites(): Promise<WebsiteListResponse> {
  try {
    // Send GET request to websites endpoint
    const response = await apiClient.get<WebsiteListResponse>('/api/websites');
    // Return the response data (contains array of websites)
    return response.data;
  } catch (error) {
    // Convert error to standardized ApiError format
    throw handleApiError(error);
  }
}

/**
 * Get website details and chunks by website ID
 * 
 * Retrieves a specific website and all its associated content chunks by ID.
 * Note: This endpoint may not be implemented in the backend yet.
 * 
 * @param id - The ID of the website to retrieve
 * @returns Promise resolving to WebsiteChunksResponse containing website and chunks
 * @throws ApiError if the request fails
 */
export async function getWebsite(id: number): Promise<WebsiteChunksResponse> {
  try {
    // Send GET request to website endpoint with ID
    const response = await apiClient.get<WebsiteChunksResponse>(`/api/websites/${id}`);
    // Return the response data (contains website and chunks)
    return response.data;
  } catch (error) {
    // Convert error to standardized ApiError format
    throw handleApiError(error);
  }
}

/**
 * Get website details and chunks by website title
 * 
 * Retrieves a website and all its associated content chunks using the website title.
 * If multiple websites have the same title, returns the most recently scraped one.
 * 
 * @param title - The title of the website to retrieve
 * @returns Promise resolving to WebsiteChunksResponse containing website and chunks
 * @throws ApiError if the request fails
 */
export async function getWebsiteByTitle(title: string): Promise<WebsiteChunksResponse> {
  try {
    // Send GET request to website-by-title endpoint with title in request body
    // Note: Using request body for GET is non-standard but matches backend implementation
    // Using axios.request with method: 'GET' to send data in request body
    const response = await apiClient.request<WebsiteChunksResponse>({
      method: 'GET',
      url: '/api/websites/title',
      data: {
        title,
      },
    });
    // Return the response data (contains website and chunks)
    return response.data;
  } catch (error) {
    // Convert error to standardized ApiError format
    throw handleApiError(error);
  }
}

/**
 * Get website details and chunks by website URL
 * 
 * Retrieves a website and all its associated content chunks using the website URL.
 * 
 * @param url - The URL of the website to retrieve
 * @returns Promise resolving to WebsiteChunksResponse containing website and chunks
 * @throws ApiError if the request fails
 */
export async function getWebsiteByUrl(url: string): Promise<WebsiteChunksResponse> {
  try {
    // Send GET request to website-by-url endpoint with URL in request body
    // Note: Using request body for GET is non-standard but matches backend implementation
    // Using axios.request with method: 'GET' to send data in request body
    const response = await apiClient.request<WebsiteChunksResponse>({
      method: 'GET',
      url: '/api/websites/url',
      data: {
        url,
      },
    });
    // Return the response data (contains website and chunks)
    return response.data;
  } catch (error) {
    // Convert error to standardized ApiError format
    throw handleApiError(error);
  }
}

/**
 * Get conversation history for a given conversation ID
 * 
 * Retrieves all messages from a conversation using the conversation ID.
 * The messages are returned in chronological order (oldest first).
 * 
 * @param conversationId - The conversation ID to retrieve history for
 * @returns Promise resolving to conversation history response containing array of messages
 * @throws ApiError if the request fails
 */
export async function getConversationHistory(
  conversationId: string
): Promise<{ conversation_history: Array<{
  id: number;
  conversation_id: string;
  message: string;
  sender: 'user' | 'assistant';
  timestamp: string;
}> }> {
  try {
    type ConversationMessage = {
      id: number;
      conversation_id: string;
      message: string;
      sender: 'user' | 'assistant';
      timestamp: string;
    };
    type ConversationHistoryResponse = {
      conversation_history: ConversationMessage[];
    }
    // Send POST request to conversation history endpoint with conversation ID in request body
    const response = await apiClient.post<ConversationHistoryResponse>('/api/chat/conversation_history', {
      conversation_id: conversationId,
    });
    //convert the response data to frontend format. For every message with show_user set to true
    //set message to only be the text
    let frontend_conversation_history: ConversationMessage[] = [];
    for (const message of response.data.conversation_history) {
      let message_contents = message.message;
      let message_contents_json = JSON.parse(message_contents) as Record<string, any>;
      if (message_contents_json.type === 'message' && message_contents_json.show_user === true){
        frontend_conversation_history.push({
          id: message.id,
          conversation_id: message.conversation_id,
          message: message_contents_json.content,
          sender: message.sender,
          timestamp: message.timestamp,
        } as ConversationMessage)
      } else if (message_contents_json.type === 'function_call_output' && message_contents_json.show_user === true){
        //Currently we don't want to display function call outputs to the user but just in case we provide this.
        frontend_conversation_history.push({
          id: message.id,
          conversation_id: message.conversation_id,
          message: message_contents_json.output,
          sender: message.sender,
          timestamp: message.timestamp,
        } as ConversationMessage)
      }
    }
    let conversation_history_res: ConversationHistoryResponse = {
      conversation_history: frontend_conversation_history,
    }
    return conversation_history_res;
    // const frontend_conversation_history = response.data.conversation_history.map((message) => {
    //   let message_contents = message.message;
    //   let message_contents_json = JSON.parse(message_contents) as Record<string, any>;
    //   if (message.show_user) {
    //     return {
    //       id: message.id,
    //       conversation_id: message.conversation_id,
    //       message: message.message,
    //     };
    //   }
    // });
    // Return the response data (contains conversation_history array)
    // return response.data;
  } catch (error) {
    // Convert error to standardized ApiError format
    throw handleApiError(error);
  }
}

/**
 * Health check endpoint
 * 
 * Checks if the backend API is running and responsive.
 * Useful for monitoring and debugging connection issues.
 * 
 * @returns Promise resolving to health status object
 * @throws ApiError if the request fails
 */
export async function healthCheck(): Promise<{ status: string }> {
  try {
    // Send GET request to health check endpoint
    const response = await apiClient.get<{ status: string }>('/api/health');
    // Return the response data (contains status: "healthy")
    return response.data;
  } catch (error) {
    // Convert error to standardized ApiError format
    throw handleApiError(error);
  }
}
