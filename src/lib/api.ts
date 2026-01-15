import axios, { AxiosInstance, AxiosError } from 'axios';
import type { ChatResponse, ScrapeResponse, WebsiteListResponse, WebsiteChunksResponse, ApiError } from '@/types';

// Get API URL from environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Create axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling utility
export function handleApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    // Type guard for response data with message property
    const responseData = axiosError.response?.data;
    const errorMessage = 
      (responseData && typeof responseData === 'object' && 'message' in responseData)
        ? (responseData as { message: string }).message
        : axiosError.message;
    
    return {
      error: axiosError.message,
      message: errorMessage,
      status: axiosError.response?.status,
    };
  }
  return {
    error: 'An unexpected error occurred',
    message: error instanceof Error ? error.message : 'Unknown error',
  };
}

// API functions
export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  try {
    const response = await apiClient.post<ChatResponse>('/api/chat/message', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

export async function scrapeWebsite(url: string): Promise<ScrapeResponse> {
  try {
    const response = await apiClient.post<ScrapeResponse>('/api/websites/scrape', {
      url,
    });
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

export async function getWebsites(): Promise<WebsiteListResponse> {
  try {
    const response = await apiClient.get<WebsiteListResponse>('/api/websites');
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

export async function getWebsite(id: number): Promise<WebsiteChunksResponse> {
  try {
    const response = await apiClient.get<WebsiteChunksResponse>(`/api/websites/${id}`);
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}

export async function healthCheck(): Promise<{ status: string }> {
  try {
    const response = await apiClient.get<{ status: string }>('/api/health');
    return response.data;
  } catch (error) {
    throw handleApiError(error);
  }
}
