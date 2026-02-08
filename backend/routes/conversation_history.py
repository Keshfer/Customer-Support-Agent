"""
Conversation History Routes

This module provides Flask routes for retrieving conversation history:
- POST /api/chat/conversation_history: Get all messages from a conversation by conversation ID

All endpoints include request validation and comprehensive error handling.
"""

import logging
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import HTTPException
from backend.services.database_service import get_conversation_history, get_all_conversation_histories, delete_conversation

# Create a Flask blueprint instance for conversation history routes
# Blueprints allow us to organize routes into logical groups
conversation_history_bp = Blueprint('conversation_history', __name__)

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_frontend_format(messages_list):
	"""
	Convert messages_list to frontend format. Removes the fields type and show_user. Only returns the content as a string
	
	Args:
		messages_list: List of messages
	
	Returns:
		List of messages in frontend format
	"""
	frontend_messages_list = []


@conversation_history_bp.route('/chat/conversation_history', methods=['POST'])
def get_conversation_history_route():
	"""
	Get conversation history for a given conversation ID.
	
	This endpoint retrieves all messages from a conversation, ordered chronologically.
	The conversation history is useful for:
	- Loading previous conversations
	- Displaying chat history to users
	- Providing context for AI responses
	
	Request Body:
		{
			"conversation_id": "uuid-string"  # Required: The conversation ID to retrieve history for
		}
	
	Returns:
		Success (200): {
			"conversation_history": [
				{
					"id": 1,
					"conversation_id": "uuid-string",
					"message": "Hello, how can I help?",
					"sender": "agent",
					"timestamp": "2024-01-01T00:00:00"
				},
				{
					"id": 2,
					"conversation_id": "uuid-string",
					"message": "I need help with my account",
					"sender": "user",
					"timestamp": "2024-01-01T00:01:00"
				}
			]
		}
		
		Error (400): Missing or invalid conversation_id parameter
		Error (404): No messages found for this conversation
		Error (415): Invalid Content-Type header
		Error (500): Database error
	
	Raises:
		HTTPException: Re-raised for proper Flask error handling
		Exception: Catches all other exceptions and returns 500 error
	"""
	try:
		# Step 1: Validate Content-Type header first
		# Check Content-Type before attempting to parse JSON
		# This provides clearer error messages
		content_type = request.headers.get('Content-Type')
		if content_type and 'application/json' not in content_type:
			# Invalid Content-Type header
			logger.warning("Invalid Content-Type header in conversation history request")
			return jsonify({'error': 'Content-Type must be application/json'}), 415
		
		# Step 2: Extract and validate request data
		# Attempt to get JSON data from request body
		# Use silent=True to return None instead of raising exception for invalid Content-Type
		# This allows us to handle the error gracefully
		data = request.get_json(silent=True)
		
		# Check if JSON parsing failed (None indicates no JSON or invalid Content-Type)
		if data is None:
			logger.warning("Missing or invalid request body in conversation history request")
			return jsonify({'error': 'Request body is required and must be valid JSON'}), 400
		
		# Step 3: Validate that request contains 'conversation_id' field
		# Extract and validate conversation_id in a single check
		conversation_id = data.get('conversation_id', '').strip()
		if not conversation_id:
			logger.warning("Missing or empty 'conversation_id' field in conversation history request")
			return jsonify({'error': 'Conversation ID is required in request body and cannot be empty'}), 400
		
		# Step 4: Retrieve conversation history from database
		# The get_conversation_history function returns a tuple: (messages_list, error)
		# On success: (messages_list, None)
		# On error: (None, error_message)
		logger.info(f"Retrieving conversation history for conversation_id: {conversation_id}")
		messages_list, error = get_conversation_history(conversation_id)

		logger.info(f"conversation history error banana: {error}")
		# Step 5: Handle database function response
		# Check if an error occurred during database retrieval
		if error:
			# Check if it's a "not found" error (no messages) vs a database error
			if "No messages found" in error:
				logger.info(f"No messages found for conversation_id: {conversation_id}")
				return jsonify({'error': error}), 404
			else:
				# Database or other error occurred
				logger.error(f"Database error retrieving conversation history: {error}")
				return jsonify({'error': error}), 500
		# Step 6: Return conversation history
		# Success case: messages_list contains the conversation history
		logger.info(f"Successfully retrieved {len(messages_list)} messages for conversation_id: {conversation_id}")
		return jsonify({'conversation_history': messages_list}), 200

	except HTTPException as e:
		# Catch HTTP exceptions (like 415 Unsupported Media Type) and return them properly
		# This handles cases where Flask/Werkzeug raises HTTP exceptions
		logger.warning(f"HTTP exception in get_conversation_history_route: {e.code} - {e.description}")
		return jsonify({'error': e.description}), e.code
	except Exception as e:
		# Catch all other exceptions and return 500 error
		# This ensures we don't expose internal errors to the client
		logger.error(f"Unexpected error in get_conversation_history_route: {e}", exc_info=True)
		return jsonify({'error': 'An unexpected error occurred while retrieving conversation history'}), 500

@conversation_history_bp.route('/chat/all_conversations', methods=['GET'])
def get_all_conversations_route():
	"""
	Get all conversation histories.
	
	This endpoint retrieves all conversations with their conversation IDs, timestamps,
	and first user messages. The conversations are ordered by most recent first.
	This is useful for displaying conversation tabs or a conversation list.
	
	Returns:
		Success (200): {
			"conversations": [
				{
					"conversation_id": "uuid-string",
					"timestamp": "2024-01-01T00:00:00",
					"first_message": "Hello, I need help"
				},
				...
			]
		}
		
		Error (404): No conversations found
		Error (500): Database error
	"""
	try:
		# Retrieve all conversation histories from database
		logger.info("Retrieving all conversation histories")
		conversations_list, error = get_all_conversation_histories()
		
		# Handle database function response
		if error:
			# Check if it's a "not found" error vs a database error
			if "No conversation histories found" in error:
				logger.info("No conversation histories found")
				return jsonify({'conversations': []}), 200
			else:
				# Database or other error occurred
				logger.error(f"Database error retrieving all conversation histories: {error}")
				#return jsonify({'error': error}), 500
				return jsonify({'error': 'An unexpected error occurred while retrieving all conversations (database)'}), 500
		
		# Return conversation histories
		logger.info(f"Successfully retrieved {len(conversations_list)} conversations")
		return jsonify({'conversations': conversations_list}), 200
		
	except Exception as e:
		# Catch all other exceptions and return 500 error
		logger.error(f"Unexpected error in get_all_conversations_route: {e}", exc_info=True)
		return jsonify({'error': 'An unexpected error occurred while retrieving all conversations'}), 500

@conversation_history_bp.route('/chat/conversation', methods=['DELETE'])
def delete_conversation_route():
	"""
	Delete a conversation by conversation ID.
	
	This endpoint deletes all messages associated with a conversation_id.
	After deletion, the conversation will no longer appear in conversation lists.
	
	Request Body:
		{
			"conversation_id": "uuid-string"  # Required: The conversation ID to delete
		}
	
	Returns:
		Success (200): {
			"message": "Conversation deleted successfully"
		}
		
		Error (400): Missing or invalid conversation_id parameter
		Error (404): No messages found for this conversation
		Error (415): Invalid Content-Type header
		Error (500): Database error
	
	Raises:
		HTTPException: Re-raised for proper Flask error handling
		Exception: Catches all other exceptions and returns 500 error
	"""
	try:
		# Step 1: Validate Content-Type header first
		content_type = request.headers.get('Content-Type')
		if content_type and 'application/json' not in content_type:
			logger.warning("Invalid Content-Type header in delete conversation request")
			return jsonify({'error': 'Content-Type must be application/json'}), 415
		
		# Step 2: Extract and validate request data
		data = request.get_json(silent=True)
		if data is None:
			logger.warning("Missing or invalid request body in delete conversation request")
			return jsonify({'error': 'Request body is required and must be valid JSON'}), 400
		
		# Step 3: Validate that request contains 'conversation_id' field
		conversation_id = data.get('conversation_id', '').strip()
		if not conversation_id:
			logger.warning("Missing or empty 'conversation_id' field in delete conversation request")
			return jsonify({'error': 'Conversation ID is required in request body and cannot be empty'}), 400
		
		# Step 4: Delete conversation from database
		logger.info(f"Deleting conversation with conversation_id: {conversation_id}")
		success, error = delete_conversation(conversation_id)
		
		# Step 5: Handle database function response
		if error:
			# Check if it's a "not found" error vs a database error
			if "No messages found" in error:
				logger.info(f"No messages found for conversation_id: {conversation_id}")
				return jsonify({'error': error}), 404
			else:
				# Database or other error occurred
				logger.error(f"Database error deleting conversation: {error}")
				return jsonify({'error': error}), 500
		
		# Step 6: Return success response
		logger.info(f"Successfully deleted conversation with conversation_id: {conversation_id}")
		return jsonify({'message': 'Conversation deleted successfully'}), 200
		
	except HTTPException as e:
		logger.warning(f"HTTP exception in delete_conversation_route: {e.code} - {e.description}")
		return jsonify({'error': e.description}), e.code
	except Exception as e:
		logger.error(f"Unexpected error in delete_conversation_route: {e}", exc_info=True)
		return jsonify({'error': 'An unexpected error occurred while deleting conversation'}), 500
