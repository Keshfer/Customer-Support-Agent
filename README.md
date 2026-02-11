# Customer-Support-Agent

An LLM-powered customer support agent designed to perform question-and-answer conversations with users. The agent analyzes user-provided web sources and provides detailed, organized, and readable answers to questions about the content from those sources.

## Video Demo

[![Watch the demo]()](https://youtu.be/NoAYPrKUTmk)

## Features

* **Website Scraping & Storage**: Scrape and store content from user-provided websites for later reference
* **Intelligent Question Answering**: Answer questions based on stored website content using semantic search and LLM reasoning
* **Conversation Management**: Create, switch between, and manage multiple conversation tabs
* **Conversation History**: Load previous conversations and maintain context across sessions
* **Mobile-Friendly Interface**: Responsive design that works seamlessly on desktop and mobile devices
* **Vector Semantic Search**: Uses embeddings to find relevant content chunks based on meaning

## Tech Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **UI Library**: React 18+
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Language**: TypeScript

### Backend
- **Framework**: Python Flask 2.3+
- **API Style**: RESTful API
- **HTTP Client**: Requests library
- **Environment Management**: python-dotenv

### AI/ML
- **LLM Provider**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-ada-002 (for vector search)
- **Python SDK**: openai library
- **Function Calling**: Custom function calling handler for LLM tool usage

### Database
- **Primary**: PostgreSQL with pgvector extension
- **Use Case**: Semantic search for relevant content chunks using vector similarity

### Web Scraping
- **API Service**: Firecrawl API
- **Python SDK**: firecrawl-py
- **Content Processing**: Markdown conversion, text extraction (handled by Firecrawl), and text chunking

## File Structure

### Frontend Components Structure

```
src/
├── app/
│   ├── globals.css          # Global CSS styles and Tailwind configuration
│   ├── page.tsx              # Main chat page component that renders the chat interface
│   └── layout.tsx            # Root layout component that wraps all pages (provides global structure and metadata)
│      
├── components/
│   ├── ChatWindow.tsx        # Main chat interface container that orchestrates all chat-related components
│   ├── ConversationLoader.tsx # Component for loading conversations by conversation ID
│   ├── ConversationTabs.tsx  # Manages conversation tabs for switching between multiple conversations
│   ├── ErrorBoundary.tsx     # Error boundary component that catches and handles errors from frontend components
│   ├── MessageList.tsx       # Component that displays the list of messages (user and agent messages)
│   ├── MessageInput.tsx      # Input field component with send button for user message entry
│   ├── MessageBubble.tsx     # Individual message component that renders a single message (user or agent) with styling
│   └── NewChatButton.tsx     # Button component that creates new chat conversations
│
├── hooks/
│   └── useChat.ts            # Custom React hook for managing chat state (messages, conversation ID, loading states, etc.)
│
├── lib/
│   └── api.ts                # API client functions that handle HTTP requests to the Flask backend
│
└── types/
    └── index.ts              # TypeScript type definitions and interfaces for messages, API responses, etc.
```

### Backend Structure

```
backend/
├── app.py                    # Flask application entry point that initializes the Flask app, registers blueprints, configures CORS, and starts the server
├── config.py                 # Configuration management module that loads environment variables, sets up database connections, and manages application settings
├── database_schema.sql       # SQL schema file for database table definitions
│
├── routes/
│   ├── chat.py               # API endpoints for chat functionality (POST /api/chat/message handles user questions and returns AI responses)
│   ├── conversation_history.py # API endpoints for conversation history (GET all conversations, GET conversation by ID, DELETE conversation)
│   ├── relevant_chunks.py    # Function for querying database to find relevant content chunks (used as LLM function call tool)
│   └── web_crawl.py          # API endpoints for website scraping (POST /api/websites/scrape, GET /api/websites, GET /api/websites/:id)
│
├── services/
│   ├── openai_service.py     # Service for interacting with OpenAI API (sending prompts to GPT, generating embeddings, handling responses)
│   ├── scraping_service.py   # Firecrawl API integration for web scraping that fetches and extracts website content
│   ├── database_service.py    # Database operations (CRUD for websites and content chunks, vector similarity search, SQL queries)
│   ├── embedding_service.py  # Service for generating vector embeddings using OpenAI's embedding API for semantic search
│   └── prompts.py            # System prompts and prompt templates for the AI agent (customer support agent instructions, context formatting)
│
├── models/
│   ├── base.py               # SQLAlchemy declarative base for database models
│   ├── website.py            # Data model for website entities (id, url, title, scraped_at, status)
│   ├── message.py            # Data model for chat messages (message content, sender, timestamp, conversation_id)
│   └── message_content.py    # Message data model for Postgres and backend communication (handles message formatting and serialization)
│
├── utils/
│   ├── function_calling.py   # Function calling handler for processing and executing LLM function calls
│   ├── text_processing.py   # Text processing utilities (cleaning HTML, chunking text into 500-1000 token pieces, preserving semantic boundaries)
│   └── validate.py           # Validation utilities (URL validation, input sanitization, data validation)
│
└── requirements.txt          # Python package dependencies file listing all required packages and their versions
```
## How to Run
0. Install NodeJs version v24.12.0

1. Set up .env file:
```
OPENAI_API_KEY=
FIRECRAWL_API_KEY=
DATABASE_URL= 
FLASK_ENV=
FLASK_DEBUG=1
POSTGRES_PASSWORD=
```
2. Run 'pip install -r requirements.txt' to install dependencies

3. Prepare Postgres database (project was developed with docker container)
Make sure you have docker installed

    1. Pull the postgres image

    ```docker pull postgres:16.11```


    2. Create and run a docker container
    ```
    docker run --name NAME_OF_CONTAINER -e POSTGRES_PASSWORD=DESIRED_PASSWORD postgres
    ```


    ```createdb database_name```

    or connect vis psql and enter

    ```CREATE database_name```

    3. Run the schema once connected to the database
    ```
    CREATE SCHEMA database_schema.sql
    ```

    4. Set the DATABASE_URL environment variable

    ```
    DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/DATABASE_NAME
    ```

4. From project root, run the Flask backend 

```
python -m backend.app
```

5. run the frontend using

```
npm run dev
```


