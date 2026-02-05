# Customer Support AI Agent - Implementation Plan

## Overview

This implementation plan outlines the step-by-step development process for building a customer support AI agent with website scraping capabilities. The plan is organized into phases, with each phase building upon the previous one.

## UI Design Reference

Based on the finAI.png reference image, the chat interface will feature:
- **Dark theme** with modern, clean aesthetics
- **Header bar** with logo, navigation controls (back arrow, menu dots, expand icon)
- **Agent messages**: Light grey bubbles with agent name/logo (e.g., "Bob • AI Agent")
- **User messages**: Orange rounded rectangular bubbles positioned on the right
- **Message input area**: Bottom input field and send button (upward arrow in white circle)

---

## Phase 1: Project Setup & Core Infrastructure

### 1.1 Backend Setup
**Estimated Time**: 2-3 hours

**Tasks**:
- [x] Initialize Python virtual environment
- [ ] Create `backend/` directory structure
- [ ] Set up `requirements.txt` with dependencies:
  - Flask 3.0.0
  - Flask-CORS 4.0.0
  - Flask-SocketIO 5.3.0 (optional)
  - openai 1.3.0
  - firecrawl-py 0.0.16
  - psycopg2-binary 2.9.9
  - pgvector 0.2.0
  - python-dotenv 1.0.0
  - sqlalchemy 2.0.23
- [ ] Ensure `.env` file in root directory contains all required variables with placeholder values that hint at what the values should look like:
  - OPENAI_API_KEY
  - FIRECRAWL_API_KEY
  - DATABASE_URL
  - FLASK_ENV
  - FLASK_DEBUG
- [ ] Create `backend/config.py`:
  - Load environment variables
  - Database connection configuration
  - API key management
- [ ] Create `backend/app.py`:
  - Initialize Flask app
  - Configure CORS
  - Register blueprints (placeholder)
  - Health check endpoint (`GET /api/health`)
- [ ] Test Flask server starts successfully

**Deliverables**:
- Working Flask server on `http://localhost:5000`
- Health check endpoint returns `{ "status": "healthy" }`

### 1.2 Frontend Setup
**Estimated Time**: 2-3 hours

**Tasks**:
- [ ] Initialize Next.js 14+ project with TypeScript
- [ ] Set up Tailwind CSS configuration
- [ ] Create `src/` directory structure:
  - `src/app/`
  - `src/components/`
  - `src/hooks/`
  - `src/lib/`
  - `src/types/`
- [ ] Create `src/app/layout.tsx`:
  - Root layout with dark theme
  - Global styles
  - Metadata configuration
- [ ] Create `src/app/page.tsx` (placeholder)
- [ ] Create `src/types/index.ts`:
  - Message interface
  - API response types
  - Website types
  - Conversation types
- [ ] Create `src/lib/api.ts`:
  - API client setup
  - Base URL configuration from environment variables
  - Error handling utilities
- [ ] Create `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:5000`
- [ ] Test Next.js dev server starts successfully

**Deliverables**:
- Next.js app running on `http://localhost:3000`
- Basic dark theme layout
- TypeScript types defined

### 1.3 Database Setup
**Estimated Time**: 1-2 hours

**Tasks**:
- [ ] Set up PostgreSQL database (local or cloud)
- [ ] Install pgvector extension
- [ ] Create database schema:
  - `websites` table
  - `content_chunks` table with vector column
  - Indexes for vector similarity search
- [ ] Create `backend/models/website.py`:
  - SQLAlchemy model for websites
- [ ] Create `backend/models/message.py`:
  - SQLAlchemy model for messages/conversations
- [ ] Test database connection from Flask app

**Deliverables**:
- Database schema created
- Models defined and tested

---

## Phase 2: Backend Core Services

### 2.1 Database Service
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Create `backend/services/database_service.py`:
  - Database connection management
  - CRUD operations for websites:
    - `create_website(url, title, status)`
    - `get_website(id)`
    - `get_all_websites()`
    - `update_website_status(id, status)`
  - CRUD operations for content chunks:
    - `create_chunk(website_id, chunk_text, chunk_index, embedding, metadata)`
    - `get_chunks_by_website(website_id)`
    - `get_chunk(id)`
  - Vector similarity search:
    - `search_similar_chunks(query_embedding, limit=5)`
  - Conversation/message storage:
    - `save_message(conversation_id, message, sender)`
    - `get_conversation_history(conversation_id)`
- [ ] Add error handling and logging
- [ ] Write unit tests for database operations

**Deliverables**:
- Complete database service with all CRUD operations
- Vector search functionality working

### 2.2 Text Processing Utilities
**Estimated Time**: 2-3 hours

**Tasks**:
<!--No need for clean_html. Firecrawl wil return clean md or json -->
~~- [ ] Create `backend/utils/text_processing.py`:
  - `clean_html(html_content)` - Remove HTML tags, clean text~~
  - `chunk_text(text, chunk_size=800, overlap=100)` - Split text into chunks
    - Split by paragraphs first
    - Then by sentences if needed
    - Preserve semantic boundaries
  - `count_tokens(text)` - Approximate token counting
- [ ] Create `backend/utils/validators.py`:
  - `validate_url(url)` - URL validation
  - `sanitize_input(text)` - Input sanitization
- [ ] Write unit tests

**Deliverables**:
- Text processing utilities ready
- Chunking strategy implemented

### 2.3 Firecrawl Scraping Service
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Create `backend/services/scraping_service.py`:
  - Initialize Firecrawl client with API key
  - `scrape_website(url)` function:
    - Call Firecrawl API
    - Extract markdown/text content
    - Get page title
    - Handle errors (timeout, invalid URL, API failures)
  - `process_scraped_content(content)`:
    - Clean content using text_processing utilities
    - Chunk content (500-1000 tokens per chunk)
    - Return chunks with metadata
- [ ] Add retry logic for API failures
- [ ] Add rate limiting considerations
- [ ] Write unit tests with mocked Firecrawl API

**Deliverables**:
- Firecrawl integration working
- Content scraping and chunking functional

### 2.4 Embedding Service
**Estimated Time**: 2-3 hours

**Tasks**:
- [ ] Create `backend/services/embedding_service.py`:
  - Initialize OpenAI client
  - `generate_embedding(text)` - Generate vector embedding for text
  - `generate_embeddings_batch(texts)` - Batch processing for multiple chunks
  - Error handling for API failures
- [ ] Add caching mechanism (don't regenerate embeddings for same content)
- [ ] Write unit tests

**Deliverables**:
- Embedding generation service ready
- Batch processing implemented

### 2.5 OpenAI Service
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Create `backend/services/prompts.py`:
  - System prompt template for customer support agent
  - Prompt formatting functions:
    - `format_chat_prompt()` - Returns system prompt/instructions (no parameters)
    - `format_scraping_confirmation_prompt(website_title)` - Returns confirmation message prompt
- [ ] Create `backend/services/openai_service.py`:
  - Initialize OpenAI client
  - `generate_response(conversation_history=None)`:
    - Get system prompt from format_chat_prompt()
    - Pass system prompt to 'instructions' parameter
    - Pass conversation_history to 'input' parameter
    - Send to OpenAI Responses API
    - Handle streaming (optional)
    - Error handling and retries
  - `generate_embedding(text)` - Wrapper for embedding service
- [ ] Add temperature and other model parameters
- [ ] Write unit tests with mocked OpenAI API

**Deliverables**:
- OpenAI integration complete
- Prompt templates ready

---

## Phase 3: Backend API Routes

### 3.1 Website Scraping Routes
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Create `backend/routes/web_crawl.py`:
  - `POST /api/websites/scrape`:
    - Validate URL
    - Check if website already exists
    - Create website record with 'pending' status
    - Call scraping_service to fetch content
    - Process and chunk content
    - Store chunks with their embeddings in database (embedding column in content_chunks table)
    - Store chunks in database
    - Update website status to 'completed'
    - Generate LLM confirmation message
    - Return response with website_id and LLM message
  ~~- `GET /api/websites`:
    - Return list of all scraped websites~~
  - `GET /api/websites/title`:
    - Return website details and associated chunks
   - `GET /api/websites/url`:
    - Return website details and associated chunks
  - Error handling for all endpoints
- [ ] Register blueprint in `app.py`
- [ ] Add request validation
- [ ] Write integration tests

**Deliverables**:
- Website scraping endpoints functional
- End-to-end scraping flow working

### 3.2 Chat Routes
**Estimated Time**: 4-5 hours

**Tasks**:
- [ ] Create `backend/routes/chat.py`:
  - `POST /api/chat/message`:
    - Validate request body
    - Get or create conversation_id
    - Save user message to database
    - Generate embedding for user question
    - Perform vector similarity search to find relevant chunks
    - Retrieve conversation history
    - Call OpenAI service to generate response (system prompt and conversation history handled separately)
    - Save agent response to database
    - Return response with conversation_id
  - Error handling and logging
- [ ] Register blueprint in `app.py`
- [ ] Add request validation
- [ ] Write integration tests

**Deliverables**:
- Chat endpoint functional
- Question answering with context retrieval working

---

## Phase 4: Frontend UI Components

### 4.1 Base Components & Styling
**Estimated Time**: 4-5 hours

**Tasks**:
- [ ] Set up Tailwind dark theme configuration
- [ ] Create color palette:
  - Dark background colors
  - Light grey for agent messages
  - Orange for user messages
  - Header grey tones
- [ ] Create `src/components/MessageBubble.tsx`:
  - Props: message, sender (user/agent), timestamp
  - Conditional styling:
    - Agent: light grey bubble, left-aligned, with logo/name
    - User: orange rounded rectangle, right-aligned
  - Message content rendering
  - Timestamp display
- [ ] Create `src/components/MessageInput.tsx`:
  - Input field with placeholder "Input text here"
  - Send button (upward arrow in white circle)
  - Enter key to send
  - Disabled state during loading and when agent is generating a response
- [ ] Create basic styling utilities

**Deliverables**:
- Base components styled to match design
- Dark theme implemented

### 4.2 Chat Interface Components
**Estimated Time**: 5-6 hours

**Tasks**:
- [ ] Create `src/components/ChatWindow.tsx`:
  - Main container for chat interface
  - Header component:
    -title (Customer Support Agent)
    <!-- - Back arrow icon
    - Menu dots icon
    - Expand/fullscreen icon -->
  - Message list area (scrollable)
  - Message input area at bottom
  - Layout matching finAI.png design
- [ ] Create `src/components/MessageList.tsx`:
  - Render list of messages
  - Auto-scroll to bottom on new messages
  - Loading indicator for agent responses
  - Empty state when no messages
<!-- - [ ] Create `src/components/WebsiteInput.tsx`:
  - URL input field
  - Submit button
  - Loading state during scraping
  - Success/error notifications -->
- [ ] Integrate all components in ChatWindow

**Deliverables**:
- Complete chat interface matching design
- All UI components functional

### 4.3 State Management & Hooks
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Create `src/hooks/useChat.ts`:
  - State management:
    - messages array
    - conversation_id
    - loading states
    - error states
  - Functions:
    - `sendMessage(message)` - Send user message
    - `loadConversation(conversation_id)` - Load conversation history
  - Auto-save conversation_id to localStorage
- [ ] Update `src/lib/api.ts`:
  - `sendChatMessage(message, conversation_id)`
  - `getWebsites()`
  - `getWebsite(id)`
  - Error handling
- [ ] Create React Context for chat state (optional, if using Context API)
- [ ] Add loading and error states to UI

**Deliverables**:
- Chat state management working
- API integration complete

### 4.4 Main Page Integration
**Estimated Time**: 2-3 hours

**Tasks**:
- [ ] Update `src/app/page.tsx`:
  - Render ChatWindow component
  - Integrate useChat hook
  - Handle website URL detection in messages
  - Error boundary
- [ ] Add responsive design considerations
- [ ] Test full chat flow

**Deliverables**:
- Complete chat interface functional
- End-to-end user flow working

---

## Phase 5: Enhanced Features

### 5.1 Conversation History
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Update chat endpoint to properly handle conversation_id
- [ ] Add conversation list/selector in UI (optional)
- [ ] Load conversation history on page load
- [ ] Persist conversations in database
- [ ] Add conversation management (delete, rename)

**Deliverables**:
- Conversation history working
- Users can continue previous conversations

<!-- ### 5.2 Website URL Detection
**Estimated Time**: 2-3 hours

**Tasks**:
- [ ] Add URL detection in chat messages
- [ ] Auto-trigger scraping when URL detected
- [ ] Show scraping progress in chat
- [ ] Display confirmation message from LLM

**Deliverables**:
- Automatic website scraping from chat messages -->

### 5.3 Error Handling & User Feedback
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Add comprehensive error handling:
  - Network errors
  - API errors
  - Scraping failures
  - Database errors
- [ ] Add user-friendly error messages
  - Toast notifications
  - Inline error messages
- [ ] Add retry mechanisms
- [ ] Add loading indicators:
  - Typing indicator for agent
  - Scraping progress indicator

**Deliverables**:
- Robust error handling
- Clear user feedback

### 5.4 Performance Optimization
**Estimated Time**: 2-3 hours

**Tasks**:
- [ ] Implement embedding caching
- [ ] Optimize database queries
- [ ] Add connection pooling
- [ ] Frontend optimizations:
  - Code splitting
  - Lazy loading
  - Memoization where needed

**Deliverables**:
- Improved performance
- Faster response times

---

## Phase 6: Testing & Polish

### 6.1 Backend Testing
**Estimated Time**: 4-5 hours

**Tasks**:
- [ ] Write unit tests for all services:
  - database_service
  - scraping_service
  - embedding_service
  - openai_service
  - text_processing utilities
- [ ] Write integration tests for API endpoints
- [ ] Test error scenarios
- [ ] Test edge cases (empty content, very long content, etc.)

**Deliverables**:
- Comprehensive test suite
- High test coverage

### 6.2 Frontend Testing
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Write component tests
- [ ] Write hook tests
- [ ] Write integration tests for chat flow
- [ ] Test error states
- [ ] Test responsive design

**Deliverables**:
- Frontend tests complete

### 6.3 UI/UX Polish
**Estimated Time**: 4-5 hours

**Tasks**:
- [ ] Add animations/transitions:
  - Message appearance
  - Loading states

**Deliverables**:
- Polished, production-ready UI

### 6.4 Documentation
**Estimated Time**: 2-3 hours

**Tasks**:
- [ ] Update README.md with:
  - Setup instructions
  - Environment variables
  - Running the application
  - API documentation
- [ ] Add code comments
- [ ] Document API endpoints
- [ ] Add troubleshooting guide

**Deliverables**:
- Complete documentation

---

## Phase 7: Optional Enhancements

### 7.1 WebSocket Support (Optional)
**Estimated Time**: 4-5 hours

**Tasks**:
- [ ] Set up Flask-SocketIO
- [ ] Create `src/hooks/useWebSocket.ts`
- [ ] Implement real-time message updates
- [ ] Add typing indicators
- [ ] Streaming responses (token-by-token)

**Deliverables**:
- Real-time chat functionality

### 7.2 Side Panel Analytics (Optional)
**Estimated Time**: 3-4 hours

**Tasks**:
- [ ] Create analytics panel component
- [ ] Add metrics display (matching finAI.png)
- [ ] Add configuration options
- [ ] Toggle panel visibility

**Deliverables**:
- Analytics panel matching design

### 7.3 Advanced Features (Future)
- Multi-language support
- File upload support (PDFs, documents)
- User authentication
- Admin dashboard
- Voice input/output
- Multi-website knowledge base

---

## Development Timeline Estimate

**Total Estimated Time**: 60-75 hours

**Phase Breakdown**:
- Phase 1: 5-8 hours
- Phase 2: 13-18 hours
- Phase 3: 7-9 hours
- Phase 4: 14-18 hours
- Phase 5: 10-14 hours
- Phase 6: 9-12 hours
- Phase 7: 7-9 hours (optional)

**Recommended Approach**:
- Work through phases sequentially
- Test each phase before moving to next
- Commit code after each major milestone
- Review and refactor as needed

---

## Key Implementation Notes

### Code Quality
- Follow TypeScript best practices
- Use proper error handling
- Add logging for debugging
- Keep functions small and focused
- Write tests as you go

### Security
- Never commit API keys
- Validate all inputs
- Sanitize user data
- Use environment variables
- Implement rate limiting

### Performance
- Cache embeddings
- Optimize database queries
- Use connection pooling
- Implement pagination for large datasets

---

## Success Criteria

The implementation is complete when:
1. ✅ Users can send website URLs via chat
2. ✅ Websites are scraped and stored in database
3. ✅ Users can ask questions and receive AI responses
4. ✅ Responses are based on scraped website content
5. ✅ UI matches finAI.png design
6. ✅ All API endpoints are functional
7. ✅ Error handling is comprehensive
8. ✅ Application is tested and documented

---

## Next Steps

1. Review this implementation plan
2. Set up development environment
3. Begin Phase 1: Project Setup
4. Follow phases sequentially
5. Test thoroughly at each phase
6. Iterate and improve based on testing
