#!/usr/bin/env python3
"""
Test script for backend/routes/chat.py

This script tests the chat message endpoint:
- POST /api/chat/message - Chat message endpoint

It uses Flask's test client to simulate HTTP requests and mocks external services
(embedding_service, openai_service, database_service) to ensure tests are fast
and isolated.

Run from project root:
	python backend/routes/test_chat.py

Prerequisites:
	- Flask app must be configured (config.py)
	- Database service functions must be correctly implemented
	- Embedding and OpenAI services must be correctly implemented
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
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

class ChatRoutesTestCase(unittest.TestCase):
	"""
	Test suite for the chat blueprint endpoints.
	"""
	
	def setUp(self):
		"""
		Set up test client and mock external services before each test.
		
		This method is called before each test method. It:
		1. Creates a Flask test client
		2. Mocks all external service dependencies
		3. Ensures the blueprint is registered for testing
		"""
		self.app = app.test_client()
		self.app.testing = True
		
		# Mock external services to isolate endpoint testing
		# We need to patch the modules where the functions are *used*, not where they are defined.
		# For example, save_message is used in chat.py, so we patch backend.routes.chat.save_message
		
		self.patcher_save_message = patch('backend.routes.chat.save_message')
		self.mock_save_message = self.patcher_save_message.start()
		
		self.patcher_get_conversation_history = patch('backend.routes.chat.get_conversation_history')
		self.mock_get_conversation_history = self.patcher_get_conversation_history.start()
		
		self.patcher_search_similar_chunks = patch('backend.routes.chat.search_similar_chunks')
		self.mock_search_similar_chunks = self.patcher_search_similar_chunks.start()
		
		self.patcher_generate_embedding = patch('backend.routes.chat.generate_embedding')
		self.mock_generate_embedding = self.patcher_generate_embedding.start()
		
		self.patcher_generate_response = patch('backend.routes.chat.generate_response')
		self.mock_generate_response = self.patcher_generate_response.start()
		
		# Ensure the blueprint is registered for testing
		if 'chat_route' not in app.blueprints:
			app.register_blueprint(chat_bp, url_prefix='/api')
	
	def tearDown(self):
		"""
		Stop all patches after each test.
		
		This method is called after each test method to clean up mocked services.
		"""
		self.patcher_save_message.stop()
		self.patcher_get_conversation_history.stop()
		self.patcher_search_similar_chunks.stop()
		self.patcher_generate_embedding.stop()
		self.patcher_generate_response.stop()
	
	# --- Test 1: POST /api/chat/message - Basic Functionality ---
	def test_chat_message_success(self):
		"""
		Test basic chat message functionality.
		
		This test verifies:
		- User message is saved to database
		- Relevant chunks are retrieved
		- AI response is generated and saved
		- Response includes conversation_id
		"""
		print_test_header("POST /api/chat/message - Basic Functionality")
		
		try:
			# Set up mock return values
			# Mock database operations
			self.mock_save_message.return_value = (1, None)  # (message_id, error)
			self.mock_get_conversation_history.return_value = (None, "No messages found")
			
			# Mock embedding generation
			# Return a dummy embedding vector (1536 dimensions for OpenAI ada-002)
			dummy_embedding = [0.1] * 1536
			self.mock_generate_embedding.return_value = dummy_embedding
			
			# Mock vector similarity search
			# Return dummy chunks that would be found by similarity search
			dummy_chunks = [
				{
					'id': 1,
					'website_id': 1,
					'chunk_text': 'This is a relevant chunk about return policies.',
					'chunk_index': 0,
					'metadata': {'title': 'Test Website'},
					'distance': 0.2
				}
			]
			self.mock_search_similar_chunks.return_value = (dummy_chunks, None)
			
			# Mock OpenAI response generation
			self.mock_generate_response.return_value = "Based on the information available, the return policy is..."
			
			# Test 1.1: Send POST request with message
			print_info("Sending POST request with user message")
			response = self.app.post(
				'/api/chat/message',
				json={'message': 'What is the return policy?'},
				content_type='application/json'
			)
			
			# Verify response status
			assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
			print_success(f"Received 200 OK response")
			
			# Parse response JSON
			data = json.loads(response.data)
			assert 'response' in data, "Response should contain 'response' field"
			assert 'conversation_id' in data, "Response should contain 'conversation_id' field"
			assert 'chunks_used' in data, "Response should contain 'chunks_used' field"
			print_success("Response contains required fields")
			
			# Verify response content
			assert isinstance(data['response'], str), "Response should be a string"
			assert len(data['response']) > 0, "Response should not be empty"
			assert isinstance(data['conversation_id'], str), "Conversation ID should be a string"
			assert len(data['conversation_id']) > 0, "Conversation ID should not be empty"
			assert data['chunks_used'] == 1, "Should have used 1 chunk"
			print_success("Response content is valid")
			
			# Verify that save_message was called twice (user message + agent response)
			assert self.mock_save_message.call_count == 2, "save_message should be called twice"
			print_success("User message and agent response were saved to database")
			
			# Verify that generate_embedding was called
			assert self.mock_generate_embedding.called, "generate_embedding should be called"
			print_success("Embedding was generated for user question")
			
			# Verify that search_similar_chunks was called
			assert self.mock_search_similar_chunks.called, "search_similar_chunks should be called"
			print_success("Vector similarity search was performed")
			
			# Verify that generate_response was called
			assert self.mock_generate_response.called, "generate_response should be called"
			print_success("AI response was generated")
			
			print_success("Basic chat message test passed!")
			return True
			
		except AssertionError as e:
			print_error(f"Assertion failed: {e}")
			if 'response' in locals():
				print_error(f"Response status: {response.status_code}")
				print_error(f"Response body: {response.data.decode()}")
			self.fail(f"Assertion failed: {e}")
			return False
		except Exception as e:
			print_error(f"Test failed with unexpected error: {e}")
			import traceback
			traceback.print_exc()
			return False
	
	# --- Test 2: POST /api/chat/message - Request Validation ---
	def test_chat_message_missing_message(self):
		"""
		Test request validation for missing message field.
		"""
		print_test_header("POST /api/chat/message - Missing Message Field")
		
		try:
			# Test 2.1: Missing message in request body
			print_info("Testing missing message parameter")
			response = self.app.post(
				'/api/chat/message',
				json={},  # Empty JSON body
				content_type='application/json'
			)
			assert response.status_code == 400, f"Expected 400 for missing message, got {response.status_code}"
			data = json.loads(response.data)
			assert 'error' in data, "Error response should contain 'error' field"
			print_success("Missing message correctly returns 400 error")
			
			# Test 2.2: Empty message
			print_info("Testing empty message")
			response = self.app.post(
				'/api/chat/message',
				json={'message': ''},
				content_type='application/json'
			)
			assert response.status_code == 400, f"Expected 400 for empty message, got {response.status_code}"
			print_success("Empty message correctly returns 400 error")
			
			# Test 2.3: Missing Content-Type header
			print_info("Testing missing Content-Type header")
			response = self.app.post(
				'/api/chat/message',
				#json={'message': 'test'},
				data=json.dumps({'message': 'test'}),
				content_type='text/plain', # No content_type parameter
			)
			# Should return 415 or 400 depending on Flask version
			assert response.status_code in [400, 415], f"Expected 400 or 415, got {response.status_code}"
			print_success("Missing Content-Type correctly returns error")
			
			return True
			
		except AssertionError as e:
			print_error(f"Assertion failed: {e}")
			if 'response' in locals():
				print_error(f"Response status: {response.status_code}")
				print_error(f"Response body: {response.data.decode()}")
			self.fail(f"Assertion failed: {e}")
			return False
		except Exception as e:
			print_error(f"Validation test failed: {e}")
			import traceback
			traceback.print_exc()
			self.fail(f"Assertion failed: {e}")
			return False
	
	# --- Test 3: POST /api/chat/message - Conversation ID Persistence ---
	def test_conversation_id_persistence(self):
		"""
		Test that conversation_id persists across multiple messages.
		
		This test verifies:
		- Same conversation_id can be used for multiple messages
		- Conversation history is retrieved correctly
		- Multiple messages maintain context
		"""
		print_test_header("POST /api/chat/message - Conversation ID Persistence")
		
		try:
			# Set up mock return values
			self.mock_save_message.return_value = (1, None)
			dummy_embedding = [0.1] * 1536
			self.mock_generate_embedding.return_value = dummy_embedding
			self.mock_search_similar_chunks.return_value = ([], None)
			self.mock_generate_response.return_value = "Test response"
			
			# Use a fixed conversation_id for testing
			test_conversation_id = "test-conv-12345"
			
			# Test 3.1: First message in conversation
			print_info("Sending first message with conversation_id")
			self.mock_get_conversation_history.return_value = (None, "No messages found")
			
			response1 = self.app.post(
				'/api/chat/message',
				json={
					'message': 'Hello',
					'conversation_id': test_conversation_id
				},
				content_type='application/json'
			)
			
			assert response1.status_code == 200, f"First message should return 200, got {response1.status_code}"
			data1 = json.loads(response1.data)
			assert data1['conversation_id'] == test_conversation_id, "Conversation ID should match"
			print_success("First message processed successfully")
			
			# Test 3.2: Second message in same conversation
			print_info("Sending second message with same conversation_id")
			# Mock conversation history for second message
			mock_history = [
				{'id': 1, 'conversation_id': test_conversation_id, 'message': 'Hello', 'sender': 'user', 'timestamp': None},
				{'id': 2, 'conversation_id': test_conversation_id, 'message': 'Test response', 'sender': 'agent', 'timestamp': None}
			]
			self.mock_get_conversation_history.return_value = (mock_history, None)
			
			response2 = self.app.post(
				'/api/chat/message',
				json={
					'message': 'What about shipping?',
					'conversation_id': test_conversation_id
				},
				content_type='application/json'
			)
			
			assert response2.status_code == 200, f"Second message should return 200, got {response2.status_code}"
			data2 = json.loads(response2.data)
			assert data2['conversation_id'] == test_conversation_id, "Conversation ID should still match"
			print_success("Second message processed successfully with same conversation_id")
			
			# Verify that get_conversation_history was called for second message
			assert self.mock_get_conversation_history.called, "get_conversation_history should be called"
			print_success("Conversation history was retrieved for second message")
			
			return True
			
		except AssertionError as e:
			print_error(f"Assertion failed: {e}")
			if 'response1' in locals():
				print_error(f"Response 1 status: {response1.status_code}")
			if 'response2' in locals():
				print_error(f"Response 2 status: {response2.status_code}")
			self.fail(f"Assertion failed: {e}")
			return False
		except Exception as e:
			print_error(f"Conversation ID persistence test failed: {e}")
			import traceback
			traceback.print_exc()
			self.fail(f"Assertion failed: {e}")
			return False
	
	# --- Test 4: POST /api/chat/message - Error Handling ---
	def test_chat_message_error_handling(self):
		"""
		Test error handling for various failure scenarios.
		"""
		print_test_header("POST /api/chat/message - Error Handling")
		
		try:
			# Test 4.1: Database save failure
			print_info("Testing database save failure")
			self.mock_save_message.return_value = (None, "Database error")
			
			response = self.app.post(
				'/api/chat/message',
				json={'message': 'Test message'},
				content_type='application/json'
			)
			
			assert response.status_code == 500, f"Expected 500 for database error, got {response.status_code}"
			data = json.loads(response.data)
			assert 'error' in data, "Error response should contain 'error' field"
			print_success("Database save failure correctly returns 500")
			
			# Reset mocks for next test
			self.mock_save_message.return_value = (1, None)
			
			# Test 4.2: OpenAI response generation failure
			print_info("Testing OpenAI response generation failure")
			dummy_embedding = [0.1] * 1536
			self.mock_generate_embedding.return_value = dummy_embedding
			self.mock_search_similar_chunks.return_value = ([], None)
			self.mock_get_conversation_history.return_value = (None, "No messages found")
			self.mock_generate_response.return_value = None  # Simulate failure
			
			response = self.app.post(
				'/api/chat/message',
				json={'message': 'Test message'},
				content_type='application/json'
			)
			
			assert response.status_code == 500, f"Expected 500 for OpenAI failure, got {response.status_code}"
			data = json.loads(response.data)
			assert 'error' in data, "Error response should contain 'error' field"
			assert 'conversation_id' in data, "Error response should still include conversation_id"
			print_success("OpenAI failure correctly returns 500")
			
			return True
			
		except AssertionError as e:
			print_error(f"Assertion failed: {e}")
			if 'response' in locals():
				print_error(f"Response status: {response.status_code}")
				print_error(f"Response body: {response.data.decode()}")
			self.fail(f"Assertion failed: {e}")
			return False
		except Exception as e:
			print_error(f"Error handling test failed: {e}")
			import traceback
			traceback.print_exc()
			self.fail(f"Assertion failed: {e}")
			return False
	
	# --- Test 5: Endpoint Accessibility ---
	def test_endpoint_accessibility(self):
		"""
		Test that the chat endpoint is accessible via HTTP requests.
		"""
		print_test_header("Endpoint Accessibility")
		
		try:
			self.mock_save_message.return_value = (123, None)
			self.mock_search_similar_chunks.return_value = ([], None)
			self.mock_generate_embedding.return_value = [0.1] * 1536
			self.mock_generate_response.return_value = "Test response"
			self.mock_get_conversation_history.return_value = (None, "No messages found")
			
			# Test 5.1: POST /api/chat/message endpoint exists
			print_info("Testing POST /api/chat/message endpoint")
			response = self.app.post(
				'/api/chat/message',
				json={'message': 'test'},
				content_type='application/json'
			)
			# Should return 200 (success) or 500 (error), not 404 (not found)
			assert response.status_code != 404, "Endpoint should exist (not 404)"
			print_success("POST /api/chat/message endpoint is accessible")
			
			return True
			
		except AssertionError as e:
			print_error(f"Assertion failed: {e}")
			self.fail(f"Assertion failed: {e}")
			return False
		except Exception as e:
			print_error(f"Endpoint accessibility test failed: {e}")
			import traceback
			traceback.print_exc()
			self.fail(f"Assertion failed: {e}")
			return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
	"""
	Run all tests and report results.
	
	This is the main entry point for the test script. It:
	1. Runs all test functions
	2. Tracks pass/fail counts
	3. Prints a summary at the end
	4. Returns appropriate exit code for CI/CD systems
	
	Exit codes:
	- 0: All tests passed
	- 1: One or more tests failed
	"""
	print("\n" + "=" * 60)
	print("CHAT ROUTES TEST SUITE")
	print("=" * 60)
	
	# Create test suite
	loader = unittest.TestLoader()
	suite = loader.loadTestsFromTestCase(ChatRoutesTestCase)
	
	# Run tests with custom test runner
	runner = unittest.TextTestRunner(verbosity=0)
	result = runner.run(suite)
	
	# Print summary
	print("\n" + "=" * 60)
	print("TEST SUMMARY")
	print("=" * 60)
	
	print(f"\nTotal tests: {result.testsRun}")
	print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
	print(f"Failed: {len(result.failures)}")
	print(f"Errors: {len(result.errors)}")
	
	# Exit with appropriate code
	if result.wasSuccessful():
		print("\n" + "=" * 60)
		print("ALL TESTS PASSED! ✓")
		print("=" * 60)
		return 0
	else:
		print("\n" + "=" * 60)
		print("SOME TESTS FAILED! ✗")
		print("=" * 60)
		return 1

if __name__ == '__main__':
	"""
	Script entry point.
	
	When this script is run directly (not imported), it:
	1. Calls main() to run all tests
	2. Handles keyboard interrupts (Ctrl+C) gracefully
	3. Catches unexpected errors and prints traceback
	4. Exits with appropriate code for CI/CD systems
	"""
	try:
		exit_code = main()
		sys.exit(exit_code)
	except KeyboardInterrupt:
		# Handle user interruption (Ctrl+C)
		print("\n\nTest interrupted by user")
		sys.exit(1)
	except Exception as e:
		# Catch any unexpected errors that weren't handled by test functions
		print(f"\n\nUnexpected error: {e}")
		import traceback
		traceback.print_exc()
		sys.exit(1)
