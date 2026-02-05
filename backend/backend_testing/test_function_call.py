#!/usr/bin/env python3
"""
Test script for function call handling in chat.py

This script tests the function call functionality:
- Test that LLM returns a function call response for website_search and query_database tools
- Test that function calls are properly handled in the agent loop
- Test that a generated response is returned after function calls
- Test error handling for invalid function calls

Run from project root:
	python backend/backend_testing/test_function_call.py

Prerequisites:
	- Flask app must be configured (config.py)
	- All service dependencies must be available (can be mocked)
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, Mock
import json

# Add backend directory to path for module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the Flask app and blueprint
from backend.app import app
from backend.routes.chat import chat_bp

# Helper functions for test output
def print_test_header(test_name):
	"""
	Print a formatted test header for visual separation in output.
	
	Uses '=' characters to create a visual separator that makes test output easier to read.
	Each test section starts with this header to clearly identify what's being tested.
	"""
	print("\n" + "=" * 60)
	print(f"TEST: {test_name}")
	print("=" * 60)

def print_success(message):
	"""
	Print a success message with checkmark symbol.
	
	Used when a test assertion passes or a test completes successfully.
	The checkmark (✓) provides quick visual feedback that something worked correctly.
	"""
	print(f"✓ {message}")

def print_error(message):
	"""
	Print an error message with X mark symbol.
	
	Used when a test assertion fails or an unexpected error occurs.
	The X mark (✗) provides quick visual feedback that something went wrong.
	"""
	print(f"✗ {message}")

def print_info(message):
	"""
	Print an informational message with info symbol.
	
	Used to provide additional context or information during test execution.
	Not used for pass/fail, but for helpful context about what the test is doing.
	"""
	print(f"ℹ {message}")

def print_warning(message):
	"""
	Print a warning message.
	
	Used to indicate something that might be a problem but doesn't fail the test.
	For example, if the server is not running, we warn but don't fail immediately.
	"""
	print(f"⚠ {message}")


class FunctionCallTestCase(unittest.TestCase):
	"""
	Test suite for function call handling in chat routes.
	"""
	
	def setUp(self):
		"""
		Set up test client and mock external services before each test.
		
		This method is called before each test method. It:
		1. Creates a Flask test client
		2. Ensures the blueprint is registered for testing
		"""
		self.app = app.test_client()
		self.app.testing = True
		
		# Sample conversation ID for testing
		self.test_conversation_id = "test-conv-123"
		self.test_user_message = "Please scrape https://example.com and tell me about it"
	
	def create_mock_openai_response_with_function_call(self, function_name="website_search", function_args=None, call_id="call_123"):
		"""
		Create a mock OpenAI response object that contains a function call.
		
		Args:
			function_name: Name of the function being called
			function_args: Dictionary of function arguments
			call_id: ID for the function call
		
		Returns:
			Mock response object with function call structure
		"""
		if function_args is None:
			function_args = {"website_url": "https://example.com"}
		
		# Create mock tool call item
		mock_tool_call_item = MagicMock()
		mock_tool_call_item.type = "tool_call"
		mock_tool_call_item.name = function_name
		mock_tool_call_item.arguments = json.dumps(function_args)
		mock_tool_call_item.call_id = call_id
		
		# Create mock response object
		mock_response = MagicMock()
		mock_response.output = [mock_tool_call_item]
		
		return mock_response
	
	def create_mock_openai_response_with_message(self, text="This is a test response"):
		"""
		Create a mock OpenAI response object that contains only a message (no function call).
		
		Args:
			text: The response text
		
		Returns:
			Mock response object with message output
		"""
		# Create mock message item
		mock_message_item = MagicMock()
		mock_message_item.type = "message"
		mock_message_item.content = text
		
		# Create mock response object
		mock_response = MagicMock()
		mock_response.output = [mock_message_item]
		
		return mock_response
	
	def create_mock_openai_response_with_both(self, function_call_first=True):
		"""
		Create a mock OpenAI response with both function call and message.
		
		Args:
			function_call_first: If True, function call comes first, then message
		
		Returns:
			Mock response object with both function call and message
		"""
		mock_tool_call = self.create_mock_openai_response_with_function_call().output[0]
		mock_message = self.create_mock_openai_response_with_message("Response after function call").output[0]
		
		mock_response = MagicMock()
		if function_call_first:
			mock_response.output = [mock_tool_call, mock_message]
		else:
			mock_response.output = [mock_message, mock_tool_call]
		
		return mock_response
	
	@patch('backend.routes.chat.generate_response')
	@patch('backend.routes.chat.save_message')
	@patch('backend.routes.chat.get_conversation_history')
	#@patch('backend.utils.function_calling.call_function')
	@patch('backend.routes.chat.call_function')
	def test_llm_returns_function_call_response(self, mock_call_function, mock_history, mock_save, mock_generate):
		"""
		Test that the LLM returns a function call response when appropriate.
		
		This test verifies that:
		1. The OpenAI API is called
		2. The response contains a function call
		3. The function call is detected and processed
		"""
		print_test_header("Test LLM Returns Function Call Response")
		
		# Setup mocks
		mock_history.return_value = ([], None)  # No conversation history
		mock_save.return_value = (1, None)  # Successfully saved message
		mock_call_function.return_value = "Function call result"
		
		# Mock OpenAI response with function call, then message
		mock_response_1 = self.create_mock_openai_response_with_function_call()
		mock_response_2 = self.create_mock_openai_response_with_message("Final response after function call")
		
		# First call returns function call, second call returns message
		mock_generate.side_effect = [mock_response_1, mock_response_2]
		
		# Make request to chat endpoint
		response = self.app.post(
			'/api/chat/message',
			json={
				'message': self.test_user_message,
				'conversation_id': self.test_conversation_id
			},
			content_type='application/json'
		)
		
		# Verify that generate_response was called
		print_info("Verifying OpenAI service was called")
		self.assertTrue(mock_generate.called, "generate_response should be called")
		
		# Verify function was called
		print_info("Verifying function call was processed")
		self.assertTrue(mock_call_function.called, "call_function should be called")
		
		# Verify response
		self.assertEqual(response.status_code, 200, "Endpoint should return 200 OK")
		response_data = json.loads(response.data)
		self.assertIn('response', response_data, "Response should contain 'response' field")
		
		print_success("LLM function call response detected and processed correctly")
	
	@patch('backend.routes.chat.generate_response')
	@patch('backend.routes.chat.save_message')
	@patch('backend.routes.chat.get_conversation_history')
	#@patch('backend.utils.function_calling.call_function')
	@patch('backend.routes.chat.call_function')
	def test_website_search_function_call(self, mock_call_function, mock_history, mock_save, mock_generate):
		"""
		Test that website_search function call is properly handled.
		
		This test verifies that:
		1. Function calls are detected in the response
		2. The website_search function is called with correct arguments
		3. The function result is added to conversation history
		"""
		print_test_header("Test Website Search Function Call")
		
		# Setup mocks
		mock_history.return_value = ([], None)
		mock_save.return_value = (1, None)
		
		# Mock function call result
		mock_call_function.return_value = "Website scraped successfully. Title: Example Website, Chunks stored: 5"
		
		# Mock OpenAI responses: first with function call, then with message
		mock_response_1 = self.create_mock_openai_response_with_function_call(
			function_name="website_search",
			function_args={"website_url": "https://example.com"}
		)
		mock_response_2 = self.create_mock_openai_response_with_message("I've scraped the website and found useful information.")
		
		mock_generate.side_effect = [mock_response_1, mock_response_2]
		
		# Make request to chat endpoint
		response = self.app.post(
			'/api/chat/message',
			json={
				'message': "Please scrape https://example.com",
				'conversation_id': self.test_conversation_id
			},
			content_type='application/json'
		)
		
		# Verify function was called
		print_info("Verifying website_search function was called")
		self.assertTrue(mock_call_function.called, "call_function should be called")
		
		# Verify function was called with correct arguments
		call_args = mock_call_function.call_args
		self.assertEqual(call_args[0][0], "website_search", "Function name should be website_search")
		self.assertEqual(call_args[0][1]["website_url"], "https://example.com", "Function should be called with correct URL")
		
		# Verify response
		self.assertEqual(response.status_code, 200)
		response_data = json.loads(response.data)
		self.assertIn('response', response_data)
		
		print_success("Website search function call handled correctly")
	
	@patch('backend.routes.chat.generate_response')
	@patch('backend.routes.chat.save_message')
	@patch('backend.routes.chat.get_conversation_history')
	#@patch('backend.utils.function_calling.call_function')
	@patch('backend.routes.chat.call_function')
	@patch('backend.routes.relevant_chunks.query_database_for_relevant_chunks')
	def test_query_database_function_call(self, mock_query_db, mock_call_function, mock_history, mock_save, mock_generate):
		"""
		Test that query_database function call is properly handled.
		
		This test verifies that:
		1. Function calls are detected in the response
		2. The query_database function is called with correct arguments
		3. The function result is added to conversation history
		"""
		print_test_header("Test Query Database Function Call")
		
		# Setup mocks
		mock_history.return_value = ([], None)
		mock_save.return_value = (1, None)
		
		# Mock query database result
		mock_query_result = """Website Title: Example Website
Website URL: https://example.com
Chunk Content: This is example content about return policies.

"""
		mock_query_db.return_value = mock_query_result
		mock_call_function.side_effect = lambda name, args: mock_query_db(args['user_query']) if name == "query_database" else "Unknown function"
		
		# Mock OpenAI responses: first with function call, then with message
		mock_response_1 = self.create_mock_openai_response_with_function_call(
			function_name="query_database",
			function_args={"user_query": "What is the return policy?"}
		)
		mock_response_2 = self.create_mock_openai_response_with_message("Based on the information found, the return policy is...")
		
		mock_generate.side_effect = [mock_response_1, mock_response_2]
		
		# Make request to chat endpoint
		response = self.app.post(
			'/api/chat/message',
			json={
				'message': "What is the return policy?",
				'conversation_id': self.test_conversation_id
			},
			content_type='application/json'
		)
		
		# Verify function was called
		print_info("Verifying query_database function was called")
		self.assertTrue(mock_call_function.called, "call_function should be called")
		
		# Verify query_database was called
		call_args_list = mock_call_function.call_args_list
		query_db_called = any(
			call[0][0] == "query_database" 
			for call in call_args_list
		)
		self.assertTrue(query_db_called, "query_database should be called")
		
		# Verify response
		self.assertEqual(response.status_code, 200)
		response_data = json.loads(response.data)
		self.assertIn('response', response_data)
		
		print_success("Query database function call handled correctly")
	
	@patch('backend.routes.chat.generate_response')
	@patch('backend.routes.chat.save_message')
	@patch('backend.routes.chat.get_conversation_history')
	#@patch('backend.utils.function_calling.call_function')
	@patch('backend.routes.chat.call_function')
	def test_agent_loop_with_multiple_function_calls(self, mock_call_function, mock_history, mock_save, mock_generate):
		"""
		Test that the agent loop handles multiple function calls correctly.
		
		This test verifies that:
		1. The agent loop continues when function calls are made
		2. Multiple function calls can be made in sequence
		3. The loop breaks when a message is received
		4. show_user is set correctly for all message types
		"""
		print_test_header("Test Agent Loop with Multiple Function Calls")
		
		# Setup mocks
		mock_history.return_value = ([], None)
		mock_save.return_value = (1, None)
		
		# Mock function call results
		mock_call_function.side_effect = [
			"Website scraped successfully. Title: Example Website, Chunks: 5",
			"Website Title: Example Website\nWebsite URL: https://example.com\nChunk Content: Return policy information..."
		]
		
		# Mock OpenAI responses:
		# 1. First call: website_search function call
		# 2. Second call: query_database function call
		# 3. Third call: final message
		mock_response_1 = self.create_mock_openai_response_with_function_call(
			function_name="website_search",
			function_args={"website_url": "https://example.com"}
		)
		mock_response_2 = self.create_mock_openai_response_with_function_call(
			function_name="query_database",
			function_args={"user_query": "What is the return policy?"}
		)
		mock_response_3 = self.create_mock_openai_response_with_message("Based on the scraped website, the return policy is...")
		
		mock_generate.side_effect = [mock_response_1, mock_response_2, mock_response_3]
		
		# Make request to chat endpoint
		response = self.app.post(
			'/api/chat/message',
			json={
				'message': "Scrape https://example.com and tell me about the return policy",
				'conversation_id': self.test_conversation_id
			},
			content_type='application/json'
		)
		
		# Verify generate_response was called multiple times (agent loop)
		print_info("Verifying agent loop called generate_response multiple times")
		self.assertGreaterEqual(mock_generate.call_count, 2, "generate_response should be called at least twice in agent loop")
		
		# Verify function was called multiple times
		print_info("Verifying multiple function calls were made")
		print(f"mock_call_function.call_count: {mock_call_function.call_count}")
		self.assertGreaterEqual(mock_call_function.call_count, 2, "call_function should be called at least twice")
		
		# Verify show_user is set correctly for all saved messages
		print_info("Verifying show_user field in saved messages")
		function_call_outputs = 0
		messages = 0
		
		for call in mock_save.call_args_list:
			message_content = call[0][1]  # Second positional argument
			try:
				msg_dict = json.loads(message_content)
				if msg_dict.get('type') == 'function_call_output':
					function_call_outputs += 1
					self.assertFalse(
						msg_dict.get('show_user', True),
						"Function call output should have show_user=False"
					)
				elif msg_dict.get('type') == 'message':
					messages += 1
					self.assertTrue(
						msg_dict.get('show_user', False),
						"Message should have show_user=True"
					)
			except json.JSONDecodeError:
				pass
		
		# Verify we have function call outputs and messages
		self.assertGreaterEqual(function_call_outputs, 2, "Should have at least 2 function call outputs")
		self.assertEqual(messages, 1, "Should have exactly 1 message")
		
		# Verify response
		self.assertEqual(response.status_code, 200)
		response_data = json.loads(response.data)
		self.assertIn('response', response_data)
		self.assertIsNotNone(response_data['response'])
		
		print_success("Agent loop handled multiple function calls correctly with proper show_user values")
	
	@patch('backend.routes.chat.generate_response')
	@patch('backend.routes.chat.save_message')
	@patch('backend.routes.chat.get_conversation_history')
	#@patch('backend.utils.function_calling.call_function')
	@patch('backend.routes.chat.call_function')
	def test_agent_loop_breaks_on_message(self, mock_call_function, mock_history, mock_save, mock_generate):
		"""
		Test that the agent loop breaks when a message is received.
		
		This test verifies that:
		1. The agent loop continues when only function calls are present
		2. The agent loop breaks when a message is received
		3. The final message is returned to the user
		"""
		print_test_header("Test Agent Loop Breaks on Message")
		
		# Setup mocks
		mock_history.return_value = ([], None)
		mock_save.return_value = (1, None)
		mock_call_function.return_value = "Function call result"
		
		# Mock OpenAI responses:
		# 1. First call: function call only
		# 2. Second call: message (should break loop)
		mock_response_1 = self.create_mock_openai_response_with_function_call()
		mock_response_2 = self.create_mock_openai_response_with_message("Final response message")
		
		mock_generate.side_effect = [mock_response_1, mock_response_2]
		
		# Make request to chat endpoint
		response = self.app.post(
			'/api/chat/message',
			json={
				'message': self.test_user_message,
				'conversation_id': self.test_conversation_id
			},
			content_type='application/json'
		)
		
		# Verify generate_response was called exactly twice (function call, then message)
		print_info("Verifying agent loop called generate_response twice")
		self.assertEqual(mock_generate.call_count, 2, "generate_response should be called twice")
		
		# Verify response contains the final message
		self.assertEqual(response.status_code, 200)
		response_data = json.loads(response.data)
		self.assertEqual(response_data['response'], "Final response message", "Response should contain the final message")
		
		print_success("Agent loop broke correctly on message")
	
	@patch('backend.routes.chat.generate_response')
	@patch('backend.routes.chat.save_message')
	@patch('backend.routes.chat.get_conversation_history')
	#@patch('backend.utils.function_calling.call_function')
	@patch('backend.routes.chat.call_function')
	def test_unknown_function_call_error(self, mock_call_function, mock_history, mock_save, mock_generate):
		"""
		Test that unknown function calls are handled gracefully.
		
		This test verifies that:
		1. Unknown function calls return an error message
		2. The agent loop continues despite the error
		3. A response is still generated
		"""
		print_test_header("Test Unknown Function Call Error")
		
		# Setup mocks
		mock_history.return_value = ([], None)
		mock_save.return_value = (1, None)
		mock_call_function.return_value = "Error: Unknown function 'unknown_function'"
		
		# Mock OpenAI response with unknown function call, then message
		mock_response_1 = self.create_mock_openai_response_with_function_call(
			function_name="unknown_function",
			function_args={}
		)
		mock_response_2 = self.create_mock_openai_response_with_message("I encountered an error, but here's what I can tell you...")
		
		mock_generate.side_effect = [mock_response_1, mock_response_2]
		
		# Make request to chat endpoint
		response = self.app.post(
			'/api/chat/message',
			json={
				'message': self.test_user_message,
				'conversation_id': self.test_conversation_id
			},
			content_type='application/json'
		)
		
		# Verify function was called (even though it's unknown)
		self.assertTrue(mock_call_function.called, "call_function should be called even for unknown functions")
		
		# Verify response is still generated
		self.assertEqual(response.status_code, 200)
		response_data = json.loads(response.data)
		self.assertIn('response', response_data)
		
		print_success("Unknown function call handled gracefully")
	
	@patch('backend.routes.chat.generate_response')
	@patch('backend.routes.chat.save_message')
	@patch('backend.routes.chat.get_conversation_history')
	#@patch('backend.utils.function_calling.call_function')
	@patch('backend.routes.chat.call_function')
	def test_show_user_field_in_message_dicts(self, mock_call_function, mock_history, mock_save, mock_generate):
		"""
		Test that show_user field is correctly set in message dicts.
		
		This test verifies that:
		1. Function call outputs have show_user=False
		2. Messages have show_user=True
		3. The show_user field is saved to the database
		"""
		print_test_header("Test Show User Field in Message Dicts")
		
		# Setup mocks
		mock_history.return_value = ([], None)
		mock_save.return_value = (1, None)
		mock_call_function.return_value = "Function call result"
		
		# Mock OpenAI responses: first with function call, then with message
		mock_response_1 = self.create_mock_openai_response_with_function_call()
		mock_response_2 = self.create_mock_openai_response_with_message("Final response message")
		
		mock_generate.side_effect = [mock_response_1, mock_response_2]
		
		# Make request to chat endpoint
		response = self.app.post(
			'/api/chat/message',
			json={
				'message': self.test_user_message,
				'conversation_id': self.test_conversation_id
			},
			content_type='application/json'
		)
		
		# Verify save_message was called
		self.assertTrue(mock_save.called, "save_message should be called")
		
		# Get all calls to save_message
		save_calls = mock_save.call_args_list
		
		# Verify we have at least 2 calls (function call output + message)
		self.assertGreaterEqual(len(save_calls), 2, "save_message should be called at least twice")
		
		# Check the saved messages for show_user field
		function_call_output_found = False
		message_found = False
		
		for call in save_calls:
			# call[0] contains positional args, call[1] contains keyword args
			# The message content is the second positional arg (index 1)
			message_content = call[0][1]  # Second positional argument is the message content
			
			# Parse the JSON message content
			try:
				msg_dict = json.loads(message_content)
				
				if msg_dict.get('type') == 'function_call_output':
					function_call_output_found = True
					# Verify show_user is False for function call outputs
					self.assertFalse(
						msg_dict.get('show_user', True),
						"Function call output should have show_user=False"
					)
					print_info(f"Function call output has show_user={msg_dict.get('show_user')}")
					
				elif msg_dict.get('type') == 'message':
					message_found = True
					# Verify show_user is True for messages
					self.assertTrue(
						msg_dict.get('show_user', False),
						"Message should have show_user=True"
					)
					print_info(f"Message has show_user={msg_dict.get('show_user')}")
			except json.JSONDecodeError:
				# Not a JSON message (might be user message), skip
				pass
		
		# Verify both types were found
		self.assertTrue(function_call_output_found, "Function call output should be saved")
		self.assertTrue(message_found, "Message should be saved")
		
		# Verify response
		self.assertEqual(response.status_code, 200)
		response_data = json.loads(response.data)
		self.assertIn('response', response_data)
		
		print_success("Show user field correctly set in message dicts")


def run_tests():
	"""
	Run all test cases and print summary.
	
	This function:
	1. Creates a test suite from all test cases
	2. Runs the tests with verbose output
	3. Prints a summary of results
	"""
	print("\n" + "=" * 60)
	print("FUNCTION CALL HANDLING TESTS")
	print("=" * 60)
	
	# Create test suite
	loader = unittest.TestLoader()
	suite = loader.loadTestsFromTestCase(FunctionCallTestCase)
	
	# Run tests with verbose output
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	
	# Print summary
	print("\n" + "=" * 60)
	print("TEST SUMMARY")
	print("=" * 60)
	print(f"Tests run: {result.testsRun}")
	print(f"Failures: {len(result.failures)}")
	print(f"Errors: {len(result.errors)}")
	if result.testsRun > 0:
		success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
		print(f"Success rate: {success_rate:.1f}%")
	
	if result.failures:
		print("\nFailures:")
		for test, traceback in result.failures:
			print(f"  - {test}")
	
	if result.errors:
		print("\nErrors:")
		for test, traceback in result.errors:
			print(f"  - {test}")
	
	return result.wasSuccessful()


if __name__ == '__main__':
	success = run_tests()
	sys.exit(0 if success else 1)
