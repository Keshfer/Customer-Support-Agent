"""
Chat Routes

This module provides Flask routes for chat functionality:
- POST /api/chat/message: Handles user messages, retrieves relevant context, and generates AI responses

All endpoints include request validation and comprehensive error handling.
"""

import logging
import uuid
import json
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import HTTPException
from backend.services.database_service import (
	save_message,
	get_conversation_history
)
from backend.services.openai_service import generate_response
from backend.utils.function_calling import call_function
from backend.models.message_content import (
	MessageContent,
	FunctionCallOutput,
	convert_to_openai_format
)

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
		user_message_content = MessageContent(content=user_message, show_user=True)
		message_id, error = save_message(conversation_id, user_message_content.to_json(), 'user')
		
		if error:
			logger.error(f"Failed to save user message: {error}")
			return jsonify({'error': 'Failed to save user message'}), 500
		
		logger.info(f"User message saved with ID: {message_id}")
		
		# Step 3: Retrieve conversation history
		# This gets all previous messages in this conversation for context
		# The history helps the AI maintain conversation context and coherence
		logger.info(f"Retrieving conversation history for: {conversation_id}")
		conversation_history, history_error = get_conversation_history(conversation_id)
		
		# Handle conversation history retrieval
		# If history exists, we'll format it for OpenAI. If not, we'll start fresh.
		#formatted_history is a list of dicts with 'role' and 'content' keys. content can be a MessageContent instance or a FunctionCallOutput instance.
		if history_error or not conversation_history:
			logger.info("No conversation history found or error occurred - starting fresh conversation")
			# Start with just the current user message
			formatted_history = [{"role": "user", "content": user_message_content}]
		else:
			# Step 4: Format conversation history for OpenAI API
			# OpenAI expects messages in a specific format: list of dicts with 'role' and 'content'
			# Roles can be: 'user', 'assistant', or 'system'
			# We convert our database format to OpenAI's expected format
			logger.info(f"Formatting {len(conversation_history)} messages for OpenAI API")
			formatted_history = []
			
			for msg in conversation_history:
				# Parse message content - it might be JSON if it's a function call output
				try:
					msg_content = json.loads(msg["message"])
					print(f"msg_content: {msg_content}, type: {type(msg_content)}")
					
					# Determine role based on sender
					role = msg['sender']
					
					# If it's a function call output, create FunctionCallOutput instance
					if isinstance(msg_content, dict) and msg_content.get('type') == 'function_call_output':
						function_call_output = FunctionCallOutput.from_dict(msg_content)
						formatted_history.append({
							"role": role,
							"content": function_call_output
						})
					elif isinstance(msg_content, dict) and msg_content.get('type') == 'message':
						# Regular message - create MessageContent instance
						message_content = MessageContent.from_dict(msg_content)
						formatted_history.append({
							"role": role,
							"content": message_content
						})
					else:
						# Unknown message type - log error and return
						logger.error(f"Unknown message type: {msg_content.get('type') if isinstance(msg_content, dict) else 'not a dict'}")
						return jsonify({'error': 'Unknown message type'}), 500
				except (json.JSONDecodeError, KeyError) as e:
					# Log JSON decode error details
					logger.error(f"Error type: {type(e)}")
					if hasattr(e, 'msg'):
						logger.error(f"Error message: {e.msg}")
					else:
						logger.error(f"Error message: {str(e)}")
					logger.error(f"Error parsing message: {msg['message']}")
					return jsonify({'error': 'Error parsing message'}), 500
			
			logger.info(f"Formatted conversation history with {len(formatted_history)} messages")
		
		# Step 5: Agent Loop Pattern
		# This allows the LLM to make function calls, get results, and decide whether
		# to generate a response or make another function call
		logger.info("Starting agent loop")
		new_responses = []  # Append new output items to this list to save to database
		max_iterations = 10  # Prevent infinite loops
		iteration = 0
		final_response_text = ""
		
		while iteration <= max_iterations:
			iteration += 1
			logger.info(f"Agent loop iteration {iteration}/{max_iterations}")
			
			# Step 5a: Call OpenAI service to generate response
			# The OpenAI service handles:
			# - System prompt generation (instructions for the AI agent)
			# - API calls with retry logic
			# - Error handling
			# Start with empty relevant_info - LLM will use tools to get information
			relevant_info = ""  # No pre-fetched chunks, LLM must use query_database tool
			
			# Convert conversation history to OpenAI-compatible format
			# This removes show_user and other non-OpenAI fields
			openai_history = convert_to_openai_format(formatted_history)
			
			full_response = generate_response(
				conversation_history=openai_history,
				relevant_info=relevant_info,
				attempts=3,
			)
			
			if not full_response:
				logger.error("Failed to generate AI response from OpenAI service")
				return jsonify({
					'error': 'Failed to generate AI response',
					'conversation_id': conversation_id
				}), 500
			#print(f"full_response: {full_response}")
			# Step 5b: Process response output items
			# Check for function calls and messages in the response
			has_function_calls = False
			has_message = False
			
			if not hasattr(full_response, 'output') or not full_response.output:
				logger.warning("Response has no output items")
				break
			#process each element in the output list
			for item in full_response.output:
				#print(f"item: {item}, type: {type(item)}")
				if item.type == 'function_call':
					# Handle function call
					has_function_calls = True
					tool_name = item.name
					args = json.loads(item.arguments)
					
					logger.info(f"Processing function call: {tool_name} with args: {args}")
					
					# Call the function
					function_call_result = call_function(tool_name, args)
					
					# Add function call result to history and responses
					# show_user is set to False because function call outputs should not be displayed to the user
					function_call_output = FunctionCallOutput(
						call_id=item.call_id,
						output=str(function_call_result),
						show_user=False
					)
					formatted_history.append({"role": "assistant", "content": function_call_output})
					new_responses.append({"role": "assistant", "content": function_call_output})
					
					logger.info(f"Function call {tool_name} completed, result length: {len(str(function_call_result))}")
					
				elif item.type == 'message':
					# Handle message response
					#process each element in the content list
					for content_item in item.content:
						if content_item.type == "output_text":
							
							has_message = True
							message_txt = content_item.text
					
							# Add message to history and responses
							# show_user is set to True because messages should be displayed to the user
							message_content = MessageContent(
								content=message_txt,
								show_user=True
							)
							formatted_history.append({"role": "assistant", "content": message_content})
							new_responses.append({"role": "assistant", "content": message_content})
							final_response_text = message_txt
					
					logger.info(f"Received message response: {message_txt[:50]}...")
			
			# Step 5c: Decide whether to continue loop or break
			# If there are function calls, continue the loop to let LLM process the results
			# If there's a message and no function calls, break and return the response
			if has_function_calls:
				# Function calls made, continue loop to let LLM process results
				logger.info("Function calls made, continuing loop for LLM to process results")
				continue
			elif has_message and not has_function_calls:
				# Message received, break out of loop
				logger.info("Message response received, breaking out of agent loop")
				break
			else:
				# No function calls and no message - unexpected, break to avoid infinite loop
				logger.warning("No function calls or messages in response, breaking loop")
				break
		
		if iteration >= max_iterations:
			logger.warning(f"Agent loop reached max iterations ({max_iterations}), breaking")
		
		# If no final response text was found, try to extract from new_responses
		if not final_response_text and new_responses:
			last_item = new_responses[-1]
			content = last_item.get('content', '')
			if isinstance(content, MessageContent):
				logger.info(f"final_response_text from MessageContent: {content.content}")
				final_response_text = content.content
			elif isinstance(content, dict) and content.get('type') == 'message':
				final_response_text = content.get('content', '')
			elif isinstance(content, str):
				final_response_text = content

		# Step 6: Save agent response to database
		# This stores the AI's response in the messages table for future conversation context
		logger.info(f"Saving agent response to database for conversation: {conversation_id}")
		for item in new_responses:
			content = item.get("content")
			# Convert content to JSON string for database storage
			if isinstance(content, MessageContent):
				item_str = content.to_json()
			elif isinstance(content, FunctionCallOutput):
				item_str = content.to_json()
			elif isinstance(content, dict):
				# Already a dict, convert to JSON
				item_str = json.dumps(content)
			else:
				# Fallback: try to convert to string
				logger.warning(f"Unexpected content type in new_responses: {type(content)}")
				item_str = json.dumps({"type": "message", "content": str(content), "show_user": True})
			
			saved_id, error = save_message(conversation_id, item_str, 'assistant')
			
			if error:
				logger.error(f"Failed to save agent message: {error}")
				# Note: We still return the response even if saving fails
				# The user gets their answer, but it won't be in conversation history
				logger.warning("Returning response despite database save failure")
			else:
				logger.info(f"Agent message saved with ID: {saved_id}")
		
		# Step 7: Return response with conversation_id
		# Include conversation_id so the frontend can maintain conversation state
		logger.info(f"Chat message endpoint completed successfully for conversation: {conversation_id}")
		logger.info(f"final_response_text: {final_response_text}")
		return jsonify({
			'response': final_response_text,
			'conversation_id': conversation_id
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