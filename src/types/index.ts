// Message types
export interface Message {
  id?: string;
  message: string;
  sender: 'user' | 'assistant';
  timestamp?: string;
}

// API Response types
export interface ChatResponse {
  response: string;
  conversation_id: string;
}

export interface ScrapeResponse {
  website_id: number;
  status: string;
  message?: string;
}

export interface Website {
  id: number;
  url: string;
  title?: string;
  scraped_at?: string;
  status: string;
}

export interface WebsiteListResponse {
  websites: Website[];
}

export interface WebsiteChunksResponse {
  website: Website;
  chunks: ContentChunk[];
}

export interface ContentChunk {
  id: number;
  website_id: number;
  chunk_text: string;
  chunk_index: number;
  metadata?: Record<string, any>;
  created_at?: string;
}

// Conversation types
export interface Conversation {
  id: string;
  messages: Message[];
  created_at?: string;
  updated_at?: string;
}

// API Error types
export interface ApiError {
  error: string;
  message?: string;
  status?: number;
}
