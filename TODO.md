# Customer Support AI Agent - TODO List

This TODO list follows the implementation plan with alternating implementation and testing checkpoints.

---

## Phase 1: Project Setup & Core Infrastructure

### Backend Setup

- [x] **Implement**: Create `backend/` directory structure
- [x] **Implement**: Set up `requirements.txt` with all dependencies
- [x] **Test**: Verify all packages can be installed: `pip install -r requirements.txt`
- [x] **Implement**: Create `backend/config.py` to load environment variables
- [x] **Test**: Verify config loads `.env` variables correctly (print values in test script)
- [x] **Implement**: Create `backend/app.py` with Flask app, CORS, and health endpoint
- [x] **Test**: Start Flask server and verify `GET /api/health` returns `{ "status": "healthy" }`

### Frontend Setup

- [x] **Implement**: Initialize Next.js 14+ project with TypeScript
- [x] **Test**: Verify dev server starts: `npm run dev` → should see app on `http://localhost:3000`
- [x] **Implement**: Set up Tailwind CSS configuration
- [x] **Test**: Create test component with Tailwind classes to verify styling works
- [x] **Implement**: Create `src/` directory structure (app, components, hooks, lib, types)
- [x] **Implement**: Create `src/app/layout.tsx` with dark theme
- [x] **Test**: Verify dark theme is applied (background should be dark)
- [x] **Implement**: Create `src/app/page.tsx` placeholder
- [x] **Test**: Verify page renders without errors
- [x] **Implement**: Create `src/types/index.ts` with all type definitions
- [x] **Test**: Import types in test file to verify TypeScript compilation
- [x] **Implement**: Create `src/lib/api.ts` with API client setup
- [x] **Test**: Verify API client can make request to `http://localhost:5000/api/health`

### Database Setup

- [x] **Implement**: Set up PostgreSQL database and install pgvector extension
- [x] **Test**: Connect to database and run `SELECT * FROM pg_extension WHERE extname = 'vector';`
- [x] **Implement**: Create database schema (websites and content_chunks tables)
- [x] **Test**: Verify tables exist: `\dt` in psql or `SELECT table_name FROM information_schema.tables;`
- [x] **Implement**: Create `backend/models/website.py` SQLAlchemy model
- [x] **Implement**: Create `backend/models/message.py` SQLAlchemy model
- [x] **Test**: Import models in test script and verify they can be instantiated

---

## Phase 2: Backend Core Services

### Database Service

- [x] **Implement**: Create `backend/services/database_service.py` with connection management
- [x] **Test**: Test database connection (create test script that connects successfully)
- [x] **Implement**: Add CRUD operations for websites (create, get, get_all, update_status)
- [x] **Test**: Create test script that creates a website, retrieves it, and verifies data
- [x] **Implement**: Add CRUD operations for content chunks (create, get, get_by_website)
- [x] **Test**: Create test script that creates chunks and retrieves them by website_id
- [x] **Implement**: Add vector similarity search function
- [x] **Test**: Create test script with sample embeddings and verify similarity search returns correct chunks
- [x] **Implement**: Add conversation/message storage functions
- [x] **Test**: Create test script that saves messages and retrieves conversation history

### Text Processing Utilities

- [x] **Implement**: Create `backend/utils/text_processing.py`~~ with clean_html function~~
~~- [ ] **Test**: Test with sample HTML string, verify HTML tags are removed~~
- [x] **Implement**: Add chunk_text function with paragraph/sentence splitting
- [x] **Test**: Test with sample text, verify chunks are appropriate size (500-1000 tokens)
- [x] **Implement**: Add count_tokens function
- [x] **Test**: Test token counting with known text samples
- [x] **Implement**: Create `backend/utils/validators.py` with validate_url function
- [x] **Test**: Test with valid/invalid URLs, verify validation works correctly
- [x] **Implement**: Add sanitize_input function
- [x] **Test**: Test with potentially harmful input, verify sanitization

### Firecrawl Scraping Service

- [x] **Implement**: Create `backend/services/scraping_service.py` with Firecrawl client initialization
- [x] **Test**: Test Firecrawl API connection with a simple URL
- [x] **Implement**: Add scrape_website function
- [x] **Test**: Scrape a test website (e.g., example.com), verify content is extracted
- [x] **Implement**: Add process_scraped_content function with chunking
- [x] **Test**: Process scraped content, verify it's chunked correctly
- [x] **Implement**: Add error handling and retry logic
- [x] **Test**: Test with invalid URL, verify error handling works

### Embedding Service

- [x] **Implement**: Create `backend/services/embedding_service.py` with OpenAI client
- [x] **Test**: Generate embedding for test text, verify it returns vector of correct dimension (1536)
- [x] **Implement**: Add generate_embeddings_batch function
- [x] **Test**: Generate embeddings for multiple chunks, verify batch processing works
- [x] **Implement**: Add caching mechanism
- [x] **Test**: Generate embedding twice for same text, verify second call uses cache

### OpenAI Service & Prompts

- [x] **Implement**: Create `backend/services/prompts.py` with system prompt template
- [x] **Test**: Format test prompt, verify structure is correct
- [x] **Implement**: Add format_chat_prompt function
- [x] **Test**: Format prompt (system prompt only), verify it returns correct instructions
- [x] **Implement**: Add format_scraping_confirmation_prompt function
- [x] **Test**: Format confirmation prompt, verify format
- [x] **Implement**: Create `backend/services/openai_service.py` with generate_response function
- [x] **Test**: Generate response with test prompt, verify response is received
- [x] **Implement**: Add error handling and retries
- [x] **Test**: Test with invalid API key, verify error handling

---

## Phase 3: Backend API Routes

### Website Scraping Routes

- [x] **Implement**: Create `backend/routes/web_crawl.py` blueprint
- [x] **Implement**: Add `POST /api/websites/scrape` endpoint with full flow
- [x] **Test**: Send POST request to scrape a test website, verify:
  - Website record is created in database
  - Chunks are stored with embeddings
  - Response includes website_id and LLM message
~~- [ ] **Implement**: Add `GET /api/websites` endpoint
- [ ] **Test**: Send GET request, verify list of websites is returned~~
- [x] **Implement**: Add `GET /api/websites/title` endpoint
- [x] **Test**: Send GET request with website title, verify website and chunks are returned
- [x] **Implement**: Add `GET /api/websites/url` endpoint
- [x] **Test**: Send GET request with website url verify website and chunks are returned
- [x] **Implement**: Register blueprint in `app.py`
- [x] **Test**: Verify all endpoints are accessible via HTTP requests
- [x] **Implement**: Add request validation
- [x] **Test**: Send invalid requests, verify validation errors are returned

### Chat Routes

- [x] **Implement**: Create `backend/routes/chat.py` blueprint
- [x] **Implement**: Add `POST /api/chat/message` endpoint with full flow
- [x] **Test**: Send POST request with message, verify:
  - User message is saved to database
  - Relevant chunks are retrieved
  - AI response is generated and saved
  - Response includes conversation_id
- [x] **Implement**: Register blueprint in `app.py`
- [x] **Test**: Verify chat endpoint is accessible
- [x] **Implement**: Add request validation
- [x] **Test**: Send invalid requests, verify validation works
- [x] **Test**: Test conversation_id persistence (send multiple messages with same ID)

---

## Phase 4: Frontend UI Components

### Base Components & Styling

- [x] **Implement**: Set up Tailwind dark theme with color palette
- [x] **Test**: Create test page with all colors, verify they match design
- [x] **Implement**: Create `src/components/MessageBubble.tsx`
- [x] **Test**: Render MessageBubble with user and agent props, verify styling matches design
- [x] **Implement**: Create `src/components/MessageInput.tsx`
- [x] **Test**: Render MessageInput, verify input field and send button work

### Chat Interface Components

- [x] **Implement**: Create `src/components/ChatWindow.tsx` with header
- [x] **Test**: Render ChatWindow, verify header displays correctly
- [x] **Implement**: Create `src/components/MessageList.tsx`
- [x] **Test**: Render MessageList with sample messages, verify messages display correctly
- [x] **Implement**: Add auto-scroll functionality to MessageList
- [x] **Test**: Add messages programmatically, verify auto-scroll works
<!--We'll let the LLM decide to scrape via function call -->
<!-- - [ ] **Implement**: Create `src/components/WebsiteInput.tsx`
- [ ] **Test**: Render WebsiteInput, verify URL input and submit button work -->
- [x] **Implement**: Integrate all components in ChatWindow
- [x] **Test**: Render full ChatWindow, verify all components are integrated

### State Management & Hooks

- [x] **Implement**: Create `src/hooks/useChat.ts` with state management
- [x] **Test**: Use useChat hook in test component, verify state updates work
- [x] **Implement**: Add sendMessage function to useChat
- [x] **Test**: Call sendMessage, verify API request is made
<!-- No need for scrapeWebsite funciton. LLM will decide to scrape using function call tool -->
<!-- - [ ] **Implement**: Add scrapeWebsite function to useChat
- [ ] **Test**: Call scrapeWebsite, verify API request is made -->
- [x] **Implement**: Add localStorage persistence for conversation_id
- [x] **Test**: Set conversation_id, refresh page, verify it's loaded from localStorage
- [x] **Implement**: Update `src/lib/api.ts` with all API functions
- [x] **Test**: Call each API function, verify requests are made correctly

### Main Page Integration

- [x] **Implement**: Update `src/app/page.tsx` to render ChatWindow
- [x] **Test**: Open page in browser, verify ChatWindow renders
- [x] **Implement**: Integrate useChat hook in page
    -Include a component that allows entering in a conversation ID to load its conversation.
    -If there is a conversation ID stored in local storage, load the conversation everytime the page loads.
    -Include a button that clears the local storage of the conversation ID
- [x] **Test**: Verify chat functionality works on the page
- [x] **Implement**: Add error boundary
- [x] **Test**: Trigger error, verify error boundary catches it

---

## Phase 5: Enhanced Features

### Conversation History

- [x] **Implement**: Update chat endpoint to handle conversation_id properly
- [x] **Test**: Send multiple messages with same conversation_id, verify history is maintained
- [x] **Implement**: Add loadConversation function to useChat
- [x] **Test**: Load conversation history, verify messages are displayed
- [x] **Implement**: Persist conversations in database
- [x] **Test**: Create conversation, restart app, verify conversation can be loaded

### Website Scraping Tool
- [x] **Implement**: Create function tool declaration for LLM to respond with, signifying it wants to scraped the provided URL
  * The function tool should specify the url is a required parameter
- [x] **Test**: Test LLM returns a function call response
- [x] **Implement**: Create a function that gets called after the LLM returns the scraping tool declaration.
This function will:
  * Call the web_crawl.py route to scrape the provided URL.
  * Call generate_response with the user's query, assuming it is given in the same message as the website url. 
  * return the generated response to the front end.
- [x] **Test**: Test the function returns a generated response after scraping a website.

### Conversation tabs

GOAL: Have conversation tabs at the top of the page that the user can click on in order to switch to that conversation. 

- [] **Implement**: inside conversation_history.py, create a route function that calls get_all_conversation_histories and returns it.
- [] **Implement**: render tabs at the top of the page that users can click on to navigate to that conversation.
Set the title of the tab to the first message sent in that conversation.
- [] **Implement**: Upon clicking a conversation tab, load the conversation to the frontend and display the conversation. Don't reload a conversation if the user clicks on the currently active conversation tab.

<!-- ### Website URL Detection

- [ ] **Implement**: Add URL detection in chat messages
- [ ] **Test**: Send message with URL, verify URL is detected
- [ ] **Implement**: Auto-trigger scraping when URL detected
- [ ] **Test**: Send message with URL, verify scraping is triggered automatically
- [ ] **Implement**: Show scraping progress in chat
- [ ] **Test**: Trigger scraping, verify progress indicator appears -->

### Mobile friendly
- [x] **Implement**: Adjust message bubble sizes and text breaks according to screen size in order to ensure 
user and agent texts are kept within their message bubbles.


### Error Handling & User Feedback

- [ ] **Implement**: Add comprehensive error handling on backend
- [ ] **Test**: Trigger various errors (network, API, database), verify error handling works
- [ ] **Implement**: Add error handling on frontend
- [ ] **Test**: Disconnect backend, verify frontend shows error message
- [ ] **Implement**: Add loading indicators
- [ ] **Test**: Trigger actions, verify loading indicators appear

<!-- ### Performance Optimization

- [ ] **Implement**: Add embedding caching
- [ ] **Test**: Generate embedding twice for same text, verify second call is faster (uses cache)
- [ ] **Implement**: Optimize database queries
- [ ] **Test**: Measure query performance, verify improvements
- [ ] **Implement**: Add connection pooling
- [ ] **Test**: Make multiple concurrent requests, verify connections are pooled -->

---

## Phase 6: Testing & Polish

### Backend Testing

- [ ] **Implement**: Write unit tests for database_service
- [ ] **Test**: Run unit tests, verify all pass
- [ ] **Implement**: Write unit tests for scraping_service
- [ ] **Test**: Run unit tests, verify all pass
- [ ] **Implement**: Write unit tests for embedding_service
- [ ] **Test**: Run unit tests, verify all pass
- [ ] **Implement**: Write unit tests for openai_service
- [ ] **Test**: Run unit tests, verify all pass
- [ ] **Implement**: Write integration tests for API endpoints
- [ ] **Test**: Run integration tests, verify all pass

### Frontend Testing

- [ ] **Implement**: Write component tests
- [ ] **Test**: Run component tests, verify all pass
- [ ] **Implement**: Write hook tests
- [ ] **Test**: Run hook tests, verify all pass
- [ ] **Implement**: Write integration tests for chat flow
- [ ] **Test**: Run integration tests, verify all pass

### UI/UX Polish

- [ ] **Implement**: Refine styling to match finAI.png exactly
- [ ] **Test**: Compare UI with reference image, verify match
- [ ] **Implement**: Add animations/transitions
- [ ] **Test**: Trigger actions, verify animations work smoothly
- [ ] **Implement**: Improve accessibility (keyboard navigation, ARIA labels)
- [ ] **Test**: Navigate with keyboard only, verify accessibility works

### Documentation

- [ ] **Implement**: Update README.md with setup instructions
- [ ] **Test**: Follow README instructions, verify they work for new setup
- [ ] **Implement**: Add code comments
- [ ] **Implement**: Document API endpoints
- [ ] **Test**: Review documentation for completeness and accuracy

---

## Phase 7: Optional Enhancements

### WebSocket Support (Optional)

- [ ] **Implement**: Set up Flask-SocketIO
- [ ] **Test**: Verify WebSocket connection can be established
- [ ] **Implement**: Create `src/hooks/useWebSocket.ts`
- [ ] **Test**: Use WebSocket hook, verify real-time updates work
- [ ] **Implement**: Add streaming responses
- [ ] **Test**: Send message, verify response streams token-by-token

### Side Panel Analytics (Optional)

- [ ] **Implement**: Create analytics panel component
- [ ] **Test**: Render analytics panel, verify metrics display
- [ ] **Implement**: Add toggle functionality
- [ ] **Test**: Toggle panel, verify visibility changes

---

## Final Checklist

- [ ] All backend endpoints are functional
- [ ] All frontend components are functional
- [ ] End-to-end flow works (scrape website → ask question → get answer)
- [ ] Error handling is comprehensive
- [ ] Tests pass
- [ ] Documentation is complete
- [ ] Code is clean and follows best practices

---

## Testing Guidelines

### Simple Testing Approach

1. **Backend Testing**: Use simple Python scripts or curl commands to test endpoints
2. **Frontend Testing**: Use browser DevTools to verify components and network requests
3. **Integration Testing**: Manually test full user flows in the browser
4. **Unit Testing**: Write focused tests for individual functions
5. **Error Testing**: Intentionally trigger errors to verify error handling

### Quick Test Commands

```bash
# Test backend health endpoint
curl http://localhost:5000/api/health

# Test website scraping
curl -X POST http://localhost:5000/api/websites/scrape -H "Content-Type: application/json" -d '{"url": "https://example.com"}'

# Test chat endpoint
curl -X POST http://localhost:5000/api/chat/message -H "Content-Type: application/json" -d '{"message": "Hello"}'

# Run backend tests
python -m pytest backend/tests/

# Run frontend tests
npm test
```
