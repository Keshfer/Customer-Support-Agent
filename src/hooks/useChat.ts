/**
 * useChat Hook
 * 
 * Custom React hook for managing chat state and interactions.
 * Provides state management for messages, conversation ID, loading states, and error handling.
 * Includes functions for sending messages and loading conversation history.
 * Automatically persists conversation_id to localStorage.
 * 
 * @returns {Object} Hook return value containing:
 *   - messages: Array of Message objects
 *   - conversationId: Current conversation ID (string | null)
 *   - isLoading: Boolean indicating if a request is in progress
 *   - error: Error object or null
 *   - sendMessage: Function to send a user message
 *   - loadConversation: Function to load conversation history
 *   - clearError: Function to clear error state
 */

// React hooks for state management
import { useState, useEffect, useCallback } from 'react';
// API functions to send chat messages and load conversation history from backend
import { sendChatMessage, getConversationHistory } from '@/lib/api';
// Type definitions for messages
import { Message } from '@/types';

// LocalStorage key for persisting conversation ID
const CONVERSATION_ID_KEY = 'customer_support_conversation_id';

/**
 * Custom hook for managing chat functionality
 * 
 * Manages chat state including messages, conversation ID, loading states, and errors.
 * Provides functions to send messages and load conversation history.
 * Automatically loads and persists conversation ID from/to localStorage.
 */
export function useChat() {
	// State for storing all messages in the current conversation
	// Messages array contains both user and agent messages
	const [messages, setMessages] = useState<Message[]>([]);
	
	// State for storing the current conversation ID
	// Used to maintain conversation context across messages
	const [conversationId, setConversationId] = useState<string | null>(null);
	
	// State for tracking if a request is currently in progress
	// Used to disable input and show loading indicators
	const [isLoading, setIsLoading] = useState<boolean>(false);
	
	// State for storing any errors that occur during API calls
	// Error object contains error details or null if no error
	const [error, setError] = useState<Error | null>(null);

	/**
	 * Load conversation ID from localStorage on component mount
	 * This ensures conversation continuity across page refreshes
	 */
	useEffect(() => {
		// Retrieve conversation ID from browser's localStorage
		// localStorage persists data across browser sessions
		const storedConversationId = localStorage.getItem(CONVERSATION_ID_KEY);
		
		// If a conversation ID exists in localStorage, restore it
		if (storedConversationId) {
			setConversationId(storedConversationId);
		}
	}, []);

	/**
	 * Save conversation ID to localStorage whenever it changes
	 * This ensures conversation ID persists across page refreshes
	 */
	useEffect(() => {
		// Only save to localStorage if conversation ID exists
		if (conversationId) {
			// Store conversation ID in browser's localStorage
			localStorage.setItem(CONVERSATION_ID_KEY, conversationId);
		} else {
			// Remove from localStorage if conversation ID is cleared
			localStorage.removeItem(CONVERSATION_ID_KEY);
		}
	}, [conversationId]);

	/**
	 * Send a user message to the backend and receive an AI response
	 * 
	 * This function:
	 * 1. Adds the user message to the messages array immediately
	 * 2. Sends the message to the backend API
	 * 3. Receives the AI response and conversation ID
	 * 4. Adds the agent response to the messages array
	 * 5. Updates the conversation ID if a new one is returned
	 * 6. Handles any errors that occur during the process
	 * 
	 * @param message - The message text to send to the AI agent
	 * @returns Promise that resolves when the message is sent and response is received
	 */
	const sendMessage = useCallback(async (message: string) => {
		// Validate that message is not empty
		if (!message.trim()) {
			setError(new Error('Message cannot be empty'));
			return;
		}

		// Clear any previous errors
		setError(null);
		
		// Set loading state to true to indicate request is in progress
		setIsLoading(true);

		// Create user message object with current timestamp
		const userMessage: Message = {
			id: `user-${Date.now()}`,
			message: message.trim(),
			sender: 'user',
			timestamp: new Date().toISOString(),
		};

		// Add user message to messages array immediately (optimistic update)
		// This provides instant feedback to the user
		setMessages((prevMessages) => [...prevMessages, userMessage]);

		try {
			// Send message to backend API
			// The API will generate an AI response and return it along with conversation ID
			const response = await sendChatMessage(message.trim(), conversationId || undefined);

			// Update conversation ID if a new one is returned from the backend
			// This handles both new conversations and existing ones
			if (response.conversation_id) {
				setConversationId(response.conversation_id);
			}

			// Create agent response message object
			const agentMessage: Message = {
				id: `agent-${Date.now()}`,
				message: response.response,
				sender: 'agent',
				timestamp: new Date().toISOString(),
			};

			// Add agent response to messages array
			setMessages((prevMessages) => [...prevMessages, agentMessage]);
		} catch (err) {
			// Handle errors that occur during API call
			// Convert error to Error object if it's not already one
			const error = err instanceof Error ? err : new Error('Failed to send message');
			setError(error);
			
			// Remove the user message that was optimistically added
			// This provides a clean error state
			setMessages((prevMessages) => prevMessages.filter((msg) => msg.id !== userMessage.id));
		} finally {
			// Always set loading state to false when request completes
			// This ensures loading indicator is hidden regardless of success or failure
			setIsLoading(false);
		}
	}, [conversationId]);

	/**
	 * Load conversation history from the backend
	 * 
	 * This function:
	 * 1. Sends conversation ID to the backend to retrieve conversation history
	 * 2. Updates the messages array with the retrieved messages
	 * 3. Updates the conversation ID state
	 * 4. Handles any errors that occur during the process
	 * 
	 * Note: This function currently requires backend support for loading conversations.
	 * The backend endpoint for loading conversations needs to be implemented.
	 * 
	 * @param conversationIdToLoad - The conversation ID to load history for
	 * @returns Promise that resolves when conversation history is loaded
	 */
	const loadConversation = useCallback(async (conversationIdToLoad: string) => {
		// Validate that conversation ID is provided
		if (!conversationIdToLoad) {
			setError(new Error('Conversation ID is required'));
			return;
		}

		// Clear any previous errors
		setError(null);
		
		// Set loading state to true to indicate request is in progress
		setIsLoading(true);

		try {
			// Call backend API endpoint to get conversation history
			const response = await getConversationHistory(conversationIdToLoad);
			
			// Update conversation ID
			setConversationId(conversationIdToLoad);
			
			// Convert backend message format to frontend Message format
			// Backend returns messages with id as number, frontend expects string
			const loadedMessages: Message[] = response.conversation_history.map((msg) => ({
				id: msg.id.toString(),
				message: msg.message,
				sender: msg.sender as 'user' | 'agent',
				timestamp: msg.timestamp,
			}));
			
			// Update messages array with retrieved conversation history
			setMessages(loadedMessages);
		} catch (err) {
			// Handle errors that occur during API call
			const error = err instanceof Error ? err : new Error('Failed to load conversation');
			setError(error);
		} finally {
			// Always set loading state to false when request completes
			setIsLoading(false);
		}
	}, []);

	/**
	 * Clear the current error state
	 * 
	 * Allows user to dismiss error messages and retry operations
	 */
	const clearError = useCallback(() => {
		setError(null);
	}, []);

	/**
	 * Clear the current conversation
	 * 
	 * Clears all messages and conversation ID, allowing user to start a new conversation.
	 * Also removes conversation ID from localStorage.
	 */
	const clearConversation = useCallback(() => {
		// Clear messages array
		setMessages([]);
		// Clear conversation ID (this will also clear localStorage via useEffect)
		setConversationId(null);
		// Clear any errors
		setError(null);
	}, []);

	// Return hook interface with all state and functions
	return {
		messages,
		conversationId,
		isLoading,
		error,
		sendMessage,
		loadConversation,
		clearError,
		clearConversation,
	};
}
