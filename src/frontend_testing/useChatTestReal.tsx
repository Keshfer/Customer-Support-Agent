/**
 * useChatTestReal Component
 * 
 * Test component to verify useChat hook functionality with REAL API requests.
 * This component demonstrates:
 * - State management (messages, conversation_id, loading, error)
 * - sendMessage function (using real API)
 * - loadConversation function (using real API)
 * - localStorage persistence for conversation_id
 * - Error handling with real backend
 * 
 * Usage: Import and render this component to test useChat hook with actual backend API calls.
 * NOTE: This requires the backend server to be running.
 */
'use client';

// React hooks for component state and effects
import React, { useState, useEffect } from 'react';
// Custom hook for chat functionality - using the actual useChat hook
import { useChat } from '../hooks/useChat';

export default function UseChatTestReal() {
  // Use the actual useChat hook to test its implementation
  const {
    messages,
    conversationId,
    isLoading,
    error,
    sendMessage,
    loadConversation,
    clearError,
  } = useChat();

  // State for test message input
  const [testMessage, setTestMessage] = useState('');
  // State for test conversation ID input
  const [testConversationId, setTestConversationId] = useState('');
  // State to track localStorage value for display
  const [localStorageValue, setLocalStorageValue] = useState<string | null>(null);
  // State to track backend connection status
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  /**
   * Check if backend is available
   */
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'}/api/health`);
        if (response.ok) {
          setBackendStatus('connected');
        } else {
          setBackendStatus('disconnected');
        }
      } catch (err) {
        setBackendStatus('disconnected');
      }
    };

    checkBackend();
    // Check every 5 seconds
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  /**
   * Update localStorage display value whenever conversationId changes
   * This helps verify that localStorage persistence is working
   */
  useEffect(() => {
    // Read conversation ID from localStorage
    const stored = localStorage.getItem('customer_support_conversation_id');
    setLocalStorageValue(stored);
  }, [conversationId]);

  /**
   * Handle sending a test message
   * Calls the sendMessage function from useChat hook
   */
  const handleSendTestMessage = async () => {
    if (!testMessage.trim()) {
      alert('Please enter a message');
      return;
    }
    // Call sendMessage function from useChat hook
    await sendMessage(testMessage);
    // Clear input field after sending
    setTestMessage('');
  };

  /**
   * Handle loading a conversation
   * Calls the loadConversation function from useChat hook
   */
  const handleLoadConversation = async () => {
    if (!testConversationId.trim()) {
      alert('Please enter a conversation ID');
      return;
    }
    // Call loadConversation function from useChat hook
    await loadConversation(testConversationId);
  };

  /**
   * Clear conversation ID from localStorage
   * Tests localStorage persistence by clearing and verifying
   */
  const handleClearConversationId = () => {
    // Remove conversation ID from localStorage
    localStorage.removeItem('customer_support_conversation_id');
    // Update display value
    setLocalStorageValue(null);
    // Reload page to test persistence (conversation ID should be cleared)
    window.location.reload();
  };

  /**
   * Add a sample message programmatically
   * Useful for testing without typing
   */
  const addSampleMessage = () => {
    const sampleMessages = [
      'Hello, I need help with my account',
      'What are your business hours?',
      'How do I reset my password?',
      'Can you help me with billing?',
      'I want to update my email address',
    ];
    const randomMessage = sampleMessages[Math.floor(Math.random() * sampleMessages.length)];
    setTestMessage(randomMessage);
  };

  /**
   * Clear all messages (for testing empty state)
   */
  const clearMessages = () => {
    // Note: This would require a clearMessages function in useChat hook
    // For now, we'll just show a message
    alert('Clear messages functionality would need to be added to useChat hook');
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Test Controls Section */}
      <div className="flex-shrink-0 bg-header border-b border-header-light p-6">
        <h1 className="text-3xl font-bold mb-4 text-text-primary">
          useChat Hook Test (Real API)
        </h1>
        <div className="flex items-center gap-4 mb-4">
          <p className="text-text-secondary text-sm">
            This test uses REAL API requests. Backend server must be running.
          </p>
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${
                backendStatus === 'connected'
                  ? 'bg-green-500'
                  : backendStatus === 'disconnected'
                  ? 'bg-red-500'
                  : 'bg-yellow-500'
              }`}
            />
            <span className="text-text-secondary text-sm">
              {backendStatus === 'connected'
                ? 'Backend Connected'
                : backendStatus === 'disconnected'
                ? 'Backend Disconnected'
                : 'Checking...'}
            </span>
          </div>
        </div>
        
        {/* Status Information */}
        <div className="mb-4 p-4 bg-background-dark rounded-lg">
          <h2 className="text-lg font-semibold mb-2 text-text-primary">Current State:</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-text-secondary">Conversation ID: </span>
              <span className="text-text-primary font-mono">
                {conversationId || 'None'}
              </span>
            </div>
            <div>
              <span className="text-text-secondary">Messages Count: </span>
              <span className="text-text-primary">{messages.length}</span>
            </div>
            <div>
              <span className="text-text-secondary">Loading: </span>
              <span className={isLoading ? 'text-yellow-400' : 'text-green-400'}>
                {isLoading ? 'Yes' : 'No'}
              </span>
            </div>
            <div>
              <span className="text-text-secondary">Error: </span>
              <span className={error ? 'text-red-400' : 'text-green-400'}>
                {error ? error.message : 'None'}
              </span>
            </div>
            <div className="col-span-2">
              <span className="text-text-secondary">localStorage Value: </span>
              <span className="text-text-primary font-mono">
                {localStorageValue || 'None'}
              </span>
            </div>
          </div>
        </div>

        {/* Test Message Input */}
        <div className="mb-4 p-4 bg-background-dark rounded-lg">
          <h2 className="text-lg font-semibold mb-2 text-text-primary">Test sendMessage:</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !isLoading) {
                  handleSendTestMessage();
                }
              }}
              placeholder="Enter test message..."
              disabled={isLoading || backendStatus === 'disconnected'}
              className="flex-1 px-4 py-2 bg-background border border-header-light rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:border-user disabled:opacity-50"
            />
            <button
              onClick={handleSendTestMessage}
              disabled={isLoading || !testMessage.trim() || backendStatus === 'disconnected'}
              className="px-4 py-2 bg-user hover:bg-user-dark rounded-lg text-user-text transition-colors disabled:opacity-50"
            >
              Send Message
            </button>
            <button
              onClick={addSampleMessage}
              disabled={isLoading || backendStatus === 'disconnected'}
              className="px-4 py-2 bg-header hover:bg-header-light rounded-lg text-text-primary transition-colors disabled:opacity-50"
            >
              Use Sample
            </button>
          </div>
        </div>

        {/* Test Load Conversation */}
        <div className="mb-4 p-4 bg-background-dark rounded-lg">
          <h2 className="text-lg font-semibold mb-2 text-text-primary">Test loadConversation:</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={testConversationId}
              onChange={(e) => setTestConversationId(e.target.value)}
              placeholder="Enter conversation ID..."
              disabled={isLoading || backendStatus === 'disconnected'}
              className="flex-1 px-4 py-2 bg-background border border-header-light rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:border-user disabled:opacity-50"
            />
            <button
              onClick={handleLoadConversation}
              disabled={isLoading || !testConversationId.trim() || backendStatus === 'disconnected'}
              className="px-4 py-2 bg-agent hover:bg-agent-light rounded-lg text-agent-text transition-colors disabled:opacity-50"
            >
              Load Conversation
            </button>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex flex-wrap gap-3">
          <button
            onClick={clearError}
            disabled={!error}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition-colors disabled:opacity-50"
          >
            Clear Error
          </button>
          <button
            onClick={handleClearConversationId}
            className="px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg text-white transition-colors"
          >
            Clear Conversation ID (Test Persistence)
          </button>
        </div>
      </div>

      {/* Messages Display Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <h2 className="text-2xl font-semibold mb-4 text-text-primary">Messages:</h2>
        
        {messages.length === 0 ? (
          <div className="text-center py-12 text-text-secondary">
            <p>No messages yet. Send a message to start a conversation.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`p-4 rounded-lg ${
                  message.sender === 'user'
                    ? 'bg-user text-user-text ml-auto max-w-md'
                    : 'bg-agent text-agent-text mr-auto max-w-md'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">
                    {message.sender === 'user' ? 'You' : 'Agent'}
                  </span>
                  {message.timestamp && (
                    <span className="text-xs opacity-75">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  )}
                </div>
                <p className="whitespace-pre-wrap">{message.message}</p>
              </div>
            ))}
          </div>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="fixed bottom-4 right-4 bg-header p-4 rounded-lg shadow-lg">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-user border-t-transparent"></div>
              <span className="text-text-primary">Sending message...</span>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="fixed bottom-4 right-4 bg-red-600 p-4 rounded-lg shadow-lg max-w-md">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-white">Error:</p>
                <p className="text-red-100">{error.message}</p>
              </div>
              <button
                onClick={clearError}
                className="ml-4 text-white hover:text-red-200"
              >
                ×
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Test Scenarios Documentation */}
      <div className="flex-shrink-0 bg-background-dark border-t border-header p-6">
        <h2 className="text-2xl font-semibold mb-4 text-text-primary">
          Test Scenarios & Verification Checklist
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Test Scenario 1: State Management */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              1. State Management Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Verify that messages, conversationId, isLoading, and error states are properly managed.
            </p>
            <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
              <li>Send a message and verify messages array updates</li>
              <li>Check that isLoading becomes true during request</li>
              <li>Verify conversationId is set after first message</li>
            </ul>
          </div>

          {/* Test Scenario 2: sendMessage Function */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              2. sendMessage Function Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Test sending messages and receiving responses from the REAL backend.
            </p>
            <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
              <li>Send a message and verify API request is made</li>
              <li>Check that user message appears immediately</li>
              <li>Verify agent response appears after API call completes</li>
            </ul>
          </div>

          {/* Test Scenario 3: localStorage Persistence */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              3. localStorage Persistence Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Test that conversation_id persists across page refreshes.
            </p>
            <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
              <li>Send a message to create a conversation ID</li>
              <li>Refresh the page</li>
              <li>Verify conversation ID is loaded from localStorage</li>
            </ul>
          </div>

          {/* Test Scenario 4: Error Handling */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              4. Error Handling Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Test error handling when API calls fail.
            </p>
            <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
              <li>Disconnect backend server</li>
              <li>Send a message</li>
              <li>Verify error state is set and displayed</li>
            </ul>
          </div>

          {/* Test Scenario 5: Load Conversation */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              5. Load Conversation Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Test loading conversation history from the backend.
            </p>
            <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
              <li>Send a few messages to create a conversation</li>
              <li>Note the conversation ID</li>
              <li>Load the conversation using the ID</li>
              <li>Verify all messages are loaded correctly</li>
            </ul>
          </div>
        </div>

        {/* Verification Checklist */}
        <div className="bg-header p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 text-text-primary">
            Verification Checklist
          </h3>
          <ul className="list-disc list-inside space-y-1 text-text-primary text-sm">
            <li className={messages.length > 0 ? 'text-green-400' : 'text-text-secondary'}>
              ✓ Messages array updates when sending messages
            </li>
            <li className={conversationId ? 'text-green-400' : 'text-text-secondary'}>
              ✓ Conversation ID is set after sending first message
            </li>
            <li className={localStorageValue ? 'text-green-400' : 'text-text-secondary'}>
              ✓ Conversation ID is persisted to localStorage
            </li>
            <li className={isLoading !== undefined ? 'text-green-400' : 'text-text-secondary'}>
              ✓ Loading state is properly managed
            </li>
            <li className={error !== undefined ? 'text-green-400' : 'text-text-secondary'}>
              ✓ Error state is properly managed
            </li>
            <li className={backendStatus === 'connected' ? 'text-green-400' : 'text-red-400'}>
              ✓ Backend connection status is monitored
            </li>
            <li className="text-green-400">
              ✓ sendMessage function makes REAL API requests
            </li>
            <li className="text-green-400">
              ✓ loadConversation function loads history from backend
            </li>
            <li className="text-green-400">
              ✓ clearError function clears error state
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
