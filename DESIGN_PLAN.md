# Customer Support AI Agent - Design Plan

## 1. Project Overview

This project implements an intelligent customer support chat agent that can:
- Scrape and store website content from user-provided links
- Answer user questions based on the stored website information
- Provide a real-time chat interface for user-agent interaction

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────┐
│   Next.js/React │  ← Web UI (Frontend)
│   Chat Interface│
└────────┬────────┘
         │ HTTP/WebSocket
         │
┌────────▼────────┐
│  Python Flask   │  ← Backend API Server
│     Server      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────────┐
│ OpenAI│ │ Database  │
│  GPT  │ │ (Vector/  │
│  API  │ │  SQL)     │
└───────┘ └───────────┘
```

### 2.2 Component Breakdown

1. **Frontend (Next.js/React)**
   - Chat interface component
   - Message input/output display
   - Real-time message updates
   - Website link input handling

2. **Backend (Python Flask)**
   - REST API endpoints
   - WebSocket support for real-time chat (optional)
   - Request routing and validation
   - Integration with OpenAI API
   - Database operations

3. **AI Agent (OpenAI GPT)**
   - Question understanding and processing
   - Context retrieval from database
   - Response generation

4. **Database Layer**
   - Website content storage
   - Vector embeddings for semantic search (recommended)
   - Or SQL database with text-to-SQL capability

5. **Web Scraping Service**
   - Firecrawl API integration for website content extraction
   - Content cleaning and preprocessing
   - Chunking for efficient storage

## 3. Technical Stack

### 3.1 Frontend
- **Framework**: Next.js 14+ (App Router recommended)
- **UI Library**: React 18+
- **Styling**: Tailwind CSS or CSS Modules
- **State Management**: React Context API or Zustand
- **HTTP Client**: Fetch API or Axios
- **Real-time Communication**: WebSocket (Socket.io client) or Server-Sent Events

### 3.2 Backend
- **Framework**: Python Flask 2.3+
- **API Style**: RESTful API
- **Real-time**: Flask-SocketIO (optional)
- **HTTP Client**: Requests library
- **Environment Management**: python-dotenv

### 3.3 AI/ML
- **LLM Provider**: OpenAI GPT-4 or GPT-3.5-turbo
- **Embeddings**: OpenAI text-embedding-ada-002 (for vector search)
- **Python SDK**: openai library

### 3.4 Database Options

**Option A: Vector Database (Recommended)**
- **Primary**: PostgreSQL with pgvector extension
- **Alternative**: ChromaDB, Pinecone, or Weaviate
- **Use Case**: Semantic search for relevant content chunks

**Option B: SQL Database with Text-to-SQL**
- **Database**: PostgreSQL or SQLite
- **Schema**: Tables for websites, content chunks, metadata
- **Access Method**: OpenAI function calling with SQL generation

### 3.5 Web Scraping
- **API Service**: Firecrawl API
- **Python SDK**: firecrawl-py
- **Content Processing**: Markdown conversion, text extraction (handled by Firecrawl)

## 4. Database Schema Design

### 4.1 Option A: Vector Database Schema (PostgreSQL + pgvector)

```sql
-- Websites table
CREATE TABLE websites (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048) UNIQUE NOT NULL,
    title VARCHAR(512),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) -- 'pending', 'completed', 'failed'
);

-- Content chunks table with vector embeddings
CREATE TABLE content_chunks (
    id SERIAL PRIMARY KEY,
    website_id INTEGER REFERENCES websites(id),
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER,
    embedding vector(1536), -- OpenAI ada-002 dimension
    metadata JSONB, -- Additional metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for vector similarity search
CREATE INDEX ON content_chunks USING ivfflat (embedding vector_cosine_ops);
```

### 4.2 Option B: SQL Database Schema (Text-to-SQL)

```sql
-- Websites table
CREATE TABLE websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT
);

-- Content chunks table
CREATE TABLE content_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website_id INTEGER REFERENCES websites(id),
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER,
    metadata TEXT, -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for full-text search
CREATE INDEX idx_chunk_text ON content_chunks(chunk_text);
```

## 5. API Endpoint Design

### 5.1 Flask API Endpoints

```
POST   /api/chat/message
       Body: { "message": "user message", "conversation_id": "optional" }
       Response: { "response": "agent response", "conversation_id": "id" }

POST   /api/websites/scrape
       Body: { "url": "https://example.com" }
       Response: { "website_id": 123, "status": "scraping" }

GET    /api/websites
       Response: { "websites": [...] }

GET    /api/websites/:id
       Response: { "website": {...}, "chunks": [...] }

GET    /api/health
       Response: { "status": "healthy" }
```

### 5.2 WebSocket Events (Optional)

```
Client → Server:
  - 'message': Send chat message
  - 'scrape_website': Request website scraping

Server → Client:
  - 'message_response': Receive agent response
  - 'scraping_progress': Update on scraping status
  - 'error': Error notifications
```

## 6. Data Flow

### 6.1 Website Scraping Flow

```
1. User sends website URL via chat
2. Frontend sends POST /api/websites/scrape
3. Flask server validates URL
4. Scraping service calls Firecrawl API to fetch and extract website content
5. Content is cleaned and chunked (500-1000 tokens per chunk)
6. Chunks are stored in database
7. If using vector DB: Generate embeddings for each chunk
8. Store embeddings in database
9. Return success response to frontend with LLM response notifying the user it is ready for questions.
10. Frontend displays confirmation to user
```

### 6.2 Question Answering Flow

```
1. User sends question via chat interface
2. Frontend sends POST /api/chat/message with question
3. Flask server receives request
4. Server queries database for relevant content:
   - Option A: Vector similarity search using question embedding
   - Option B: Text-to-SQL query generation via OpenAI
5. Retrieve top-k most relevant chunks
6. Construct prompt with:
   - System prompt (agent instructions)
   - Retrieved context chunks
   - User question
   - Conversation history (if applicable)
7. Send prompt to OpenAI GPT API
8. Receive response from GPT
9. Return response to frontend
10. Frontend displays agent response
```

## 7. Implementation Details

### 7.1 Frontend Components Structure

```
src/
├── app/
│   ├── page.tsx              # Main chat page
│   ├── layout.tsx            # Root layout
│   └── api/                  # API routes (if needed)
├── components/
│   ├── ChatWindow.tsx        # Main chat interface
│   ├── MessageList.tsx       # Display messages
│   ├── MessageInput.tsx      # Input field with send button
│   ├── MessageBubble.tsx     # Individual message component
│   └── WebsiteInput.tsx      # URL input component
├── hooks/
│   ├── useChat.ts            # Chat state management
│   └── useWebSocket.ts       # WebSocket hook (optional)
├── lib/
│   └── api.ts                # API client functions
└── types/
    └── index.ts              # TypeScript types
```

### 7.2 Backend Structure

```
backend/
├── app.py                    # Flask application entry point
├── config.py                 # Configuration management
├── routes/
│   ├── chat.py               # Chat endpoints
│   └── web_crawl.py           # Website scraping endpoints
├── services/
│   ├── openai_service.py     # OpenAI API integration
│   ├── scraping_service.py   # Firecrawl API integration for web scraping
│   ├── database_service.py   # Database operations
│   └── embedding_service.py  # Vector embedding generation
│   └── prompts.py  		  #System prompts for the agent
├── models/
│   ├── website.py            # Website data model
│   └── message.py            # Message data model
├── utils/
│   ├── text_processing.py    # Text cleaning, chunking
│   └── validators.py         # URL validation, etc.
└── requirements.txt          # Python dependencies
```

### 7.3 Prompt Engineering

**System Prompt Template:**
```
You are a helpful customer support AI agent. Your role is to answer questions 
based on the information fetched from your database. 

Guidelines:
- Only answer questions based on the information fetched from your database
- If you can't find the relevant information, politely say you don't have that information
- Prompt the user to provide the relevant information through a website link if the answer is not in the context
- Be concise and helpful
- Use the tools available to you to satisfy the above guidelines
```

**Note:** The system prompt is passed to the OpenAI API via the `instructions` parameter. 
The conversation history is passed separately via the `input` parameter.

### 7.4 Content Chunking Strategy

- **Chunk Size**: 500-1000 tokens per chunk
- **Overlap**: 50-100 tokens between chunks (for context preservation)
- **Method**: 
  - Split by paragraphs first
  - Then by sentences if needed
  - Preserve semantic boundaries

## 8. Security Considerations

1. **Input Validation**
   - Validate URLs before scraping
   - Sanitize user inputs
   - Rate limiting on API endpoints

2. **API Security**
   - Environment variables for API keys
   - CORS configuration

3. **Web Scraping**
   - Firecrawl API key security
   - Rate limiting for API calls
   - Error handling for inaccessible sites and API failures

4. **Data Privacy**
   - Secure storage of scraped content
   - User data protection
   - API key security

## 9. Error Handling

### 9.1 Frontend Error Handling
- Network error handling
- Loading states
- User-friendly error messages
- Retry mechanisms

### 9.2 Backend Error Handling
- Invalid URL handling
- Scraping failures
- Database connection errors
- OpenAI API errors
- Timeout handling

## 10. Performance Optimization

1. **Caching**
   - Cache frequently accessed website content
   - Cache embeddings (don't regenerate for same content)

2. **Async Operations**
   - Async scraping operations
   - Background processing for embeddings

3. **Database Optimization**
   - Proper indexing
   - Connection pooling
   - Query optimization

4. **Frontend Optimization**
   - Code splitting
   - Lazy loading
   - Optimistic UI updates

## 11. Development Phases

### Phase 1: Core Infrastructure
- Set up Next.js project
- Set up Flask backend
- Basic database setup
- Simple chat UI

### Phase 2: AI Integration
- OpenAI API integration
- Basic question answering
- Context retrieval

### Phase 3: Web Scraping
- Implement scraping service
- Content processing and chunking
- Database storage

### Phase 4: Enhanced Features
- Vector embeddings (if Option A)
- Improved chunking strategy
- Conversation history
- Better prompt engineering

### Phase 5: Polish & Optimization
- Error handling
- Performance optimization
- UI/UX improvements
- Testing

## 12. Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Backend (.env)
```
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
DATABASE_URL=postgresql://user:pass@localhost/dbname
FLASK_ENV=development
FLASK_DEBUG=True
```

## 13. Testing Strategy

1. **Unit Tests**
   - Scraping service tests
   - Database service tests
   - Text processing utilities

2. **Integration Tests**
   - API endpoint tests
   - Database integration
   - OpenAI API mocking

3. **End-to-End Tests**
   - Full user flow tests
   - Chat interaction tests

## 14. Deployment Considerations

1. **Frontend Deployment**
   - Vercel (recommended for Next.js)
   - Or any static hosting service

2. **Backend Deployment**
   - Python hosting (Heroku, Railway, Render)
   - Or containerized deployment (Docker)

3. **Database**
   - Managed PostgreSQL (Supabase, Neon, etc.)
   - Or self-hosted database

## 15. Future Enhancements

1. **Multi-language support**
2. **File upload support** (PDFs, documents)
3. **User authentication and sessions**
4. **Analytics and monitoring**
5. **Admin dashboard for managing websites**
6. **Streaming responses** (token-by-token)
7. **Voice input/output**
8. **Multi-website knowledge base**

## 16. Dependencies

### Frontend (package.json)
```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "axios": "^1.6.0",
    "socket.io-client": "^4.5.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^3.3.0"
  }
}
```

### Backend (requirements.txt)
```
Flask==3.0.0
Flask-CORS==4.0.0
Flask-SocketIO==5.3.0
openai==1.3.0
firecrawl-py==0.0.16
psycopg2-binary==2.9.9
pgvector==0.2.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
```

---

## Summary

This design plan outlines a complete customer support AI agent system with:
- **Frontend**: Next.js/React chat interface
- **Backend**: Python Flask API server
- **AI**: OpenAI GPT for intelligent responses
- **Database**: Vector database (recommended) or SQL with text-to-SQL
- **Core Features**: Website scraping, content storage, and intelligent Q&A

The architecture is scalable, maintainable, and follows best practices for modern web applications.
