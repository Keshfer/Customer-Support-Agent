"""
Chat Routes

This module provides Flask routes for chat functionality:
- POST /api/chat/message: Handles user messages, retrieves relevant context, and generates AI responses

All endpoints include request validation and comprehensive error handling.
"""

import logging
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import HTTPException
from backend.services.database_service import (
	save_message,
	get_conversation_history,
	search_similar_chunks
)
from backend.services.embedding_service import generate_embedding
from backend.services.openai_service import generate_response

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Flask blueprint instance for chat routes
# Blueprints allow us to organize routes into logical groups
chat_bp = Blueprint('chat_route', __name__)



@chat_bp.route('/chat/message', methods=['POST'])
def chat_message():
	"""
	Handle user chat messages and generate AI responses.
	
	This endpoint implements the complete chat workflow:
	1. Validates the request body (message is required, conversation_id is optional)
	2. Gets or creates a conversation_id (generates UUID if not provided)
	3. Saves the user message to the database
	4. Generates an embedding for the user question
	5. Performs vector similarity search to find relevant content chunks
	6. Retrieves conversation history for context
	7. Formats conversation history for OpenAI API (role/content format)
	8. Calls OpenAI service to generate response with system prompt and conversation history
	9. Saves the agent response to the database
	10. Returns the response with conversation_id
	
	Request Body:
		{
			"message": "What is the return policy?"  # Required: User's message/question
			"conversation_id": "optional-uuid"       # Optional: Existing conversation ID
		}
	
	Returns:
		Success (200): {
			"response": "Based on the information available...",
			"conversation_id": "uuid-string",
			"chunks_used": 3  # Number of relevant chunks retrieved
		}
		
		Error (400): Missing or invalid message parameter
		Error (415): Invalid Content-Type header
		Error (500): Database, embedding, or OpenAI API errors
	
	Raises:
		HTTPException: Re-raised for proper Flask error handling
		Exception: Catches all other exceptions and returns 500 error

	Improvements:
	- chat_message always loads and formats conversation history regardless if it is the same
	conversation or different. Change this to only load and format the active conversation history once.

	"""
	try:
		# Step 1: Extract and validate request data
		# Attempt to get JSON data from request body
		# Use silent=True to return None instead of raising exception for invalid Content-Type
		# This allows us to handle the error gracefully
		data = request.get_json(silent=True)
		
		# Check if JSON parsing failed (None indicates no JSON or invalid Content-Type)
		if data is not None:
			logger.info("data is not None")
			# Check if the request has a Content-Type header
			#content_type = request.content_type
			content_type = request.headers.get('Content-Type')
			logger.info(f"content_type: {content_type}")
			if content_type and 'application/json' not in content_type:
				# Invalid Content-Type header
				logger.warning("Invalid Content-Type header in chat message request")
				return jsonify({'error': 'Content-Type must be application/json'}), 415
			elif content_type is None:
				# No Content-Type or missing request body
				logger.warning("Missing request body in chat message request")
				return jsonify({'error': 'Request body is required and must be valid JSON'}), 400
		else:
			logger.info("data is None")
			logger.warning("Missing request body in chat message request")
			return jsonify({'error': 'Request body is required and must be valid JSON'}), 400
		
		# Validate that request contains 'message' field
		if 'message' not in data:
			logger.warning("Missing 'message' field in chat message request")
			return jsonify({'error': 'Message is required in request body'}), 400
		
		# Extract and validate message content
		user_message = data.get('message', '').strip()
		if not user_message:
			logger.warning("Empty message in chat message request")
			return jsonify({'error': 'Message cannot be empty'}), 400
		
		# Extract optional conversation_id
		# If not provided, we'll generate a new UUID for this conversation
		conversation_id = data.get('conversation_id', '').strip()
		if not conversation_id:
			# Generate a new conversation ID using UUID
			# UUID4 provides random UUIDs which are suitable for conversation tracking
			conversation_id = str(uuid.uuid4())
			logger.info(f"Generated new conversation_id: {conversation_id}")
		else:
			logger.info(f"Using existing conversation_id: {conversation_id}")
		
		# Step 2: Save user message to database
		# This stores the user's message in the messages table for conversation history
		logger.info(f"Saving user message to database for conversation: {conversation_id}")
		message_id, error = save_message(conversation_id, user_message, 'user')
		
		if error:
			logger.error(f"Failed to save user message: {error}")
			return jsonify({'error': 'Failed to save user message'}), 500
		
		logger.info(f"User message saved with ID: {message_id}")
		
		# Step 3: Generate embedding for user question
		# Embeddings are vector representations used for semantic search
		# This allows us to find relevant content chunks based on meaning, not just keywords
		logger.info(f"Generating embedding for user question: {user_message[:50]}...")
		query_embedding = generate_embedding(user_message)
		
		if not query_embedding:
			logger.error("Failed to generate embedding for user question")
			# Continue without context - AI can still respond, just without retrieved context
			logger.warning("Proceeding without context chunks due to embedding failure")
			relevant_chunks = []
		else:
			# Step 4: Perform vector similarity search to find relevant chunks
			# This searches the content_chunks table for chunks with similar embeddings
			# The search returns the top-k most similar chunks (default: 5)
			logger.info("Searching for relevant content chunks using vector similarity")
			relevant_chunks, chunks_error = search_similar_chunks(query_embedding, limit=5)
			
			if chunks_error or not relevant_chunks:
				logger.warning(f"No relevant chunks found or error occurred: {chunks_error}")
				# Continue without context - AI can still respond, just without retrieved context
				relevant_chunks = []
			else:
				logger.info(f"Found {len(relevant_chunks)} relevant chunks")
		
		# Step 5: Retrieve conversation history
		# This gets all previous messages in this conversation for context
		# The history helps the AI maintain conversation context and coherence
		logger.info(f"Retrieving conversation history for: {conversation_id}")
		conversation_history, history_error = get_conversation_history(conversation_id)
		
		# Handle conversation history retrieval
		# If history exists, we'll format it for OpenAI. If not, we'll start fresh.
		if history_error or not conversation_history:
			logger.info("No conversation history found or error occurred - starting fresh conversation")
			# Start with just the current user message
			formatted_history = [{"role": "user", "content": user_message}]
		else:
			# Step 6: Format conversation history for OpenAI API
			# OpenAI expects messages in a specific format: list of dicts with 'role' and 'content'
			# Roles can be: 'user', 'assistant', or 'system'
			# We convert our database format to OpenAI's expected format
			logger.info(f"Formatting {len(conversation_history)} messages for OpenAI API")
			formatted_history = []
			
			for msg in conversation_history:
				# Map database sender field ('user' or 'agent') to OpenAI role format
				# 'agent' becomes 'assistant' for OpenAI API
				role = 'assistant' if msg['sender'] == 'agent' else 'user'
				formatted_history.append({
					"role": role,
					"content": msg['message']
				})
			
			logger.info(f"Formatted conversation history with {len(formatted_history)} messages")
		
		# Step 7: Call OpenAI service to generate response
		# The OpenAI service handles:
		# - System prompt generation (instructions for the AI agent)
		# - Conversation history formatting
		# - API calls with retry logic
		# - Error handling
		logger.info("Calling OpenAI service to generate response")
		ai_response = generate_response(conversation_history=formatted_history, attempts=3)
		
		if not ai_response:
			logger.error("Failed to generate AI response from OpenAI service")
			return jsonify({
				'error': 'Failed to generate AI response',
				'conversation_id': conversation_id
			}), 500
		
		logger.info(f"AI response generated successfully: {ai_response[:50]}...")
		
		# Step 8: Save agent response to database
		# This stores the AI's response in the messages table for future conversation context
		logger.info(f"Saving agent response to database for conversation: {conversation_id}")
		agent_message_id, error = save_message(conversation_id, ai_response, 'agent')
		
		if error:
			logger.error(f"Failed to save agent message: {error}")
			# Note: We still return the response even if saving fails
			# The user gets their answer, but it won't be in conversation history
			logger.warning("Returning response despite database save failure")
		else:
			logger.info(f"Agent message saved with ID: {agent_message_id}")
		
		# Step 9: Return response with conversation_id
		# Include conversation_id so the frontend can maintain conversation state
		# Include chunks_used count for debugging and transparency
		logger.info(f"Chat message endpoint completed successfully for conversation: {conversation_id}")
		
		return jsonify({
			'response': ai_response,
			'conversation_id': conversation_id,
			'chunks_used': len(relevant_chunks) if relevant_chunks else 0
		}), 200
		
	except HTTPException as e:
		# Catch HTTP exceptions (like 415 Unsupported Media Type) and return them properly
		# This handles cases where Flask/Werkzeug raises HTTP exceptions
		logger.warning(f"HTTP exception in chat_message: {e.code} - {e.description}")
		return jsonify({'error': e.description}), e.code
	except Exception as e:
		# Catch any unexpected errors and return generic error message
		# Log the full error for debugging while keeping response user-friendly
		logger.error(f"Unexpected error in chat_message: {e}", exc_info=True)
		return jsonify({'error': 'An unexpected error occurred while processing your message'}), 500