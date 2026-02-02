/**
 * ConversationLoader Component
 * 
 * Component that allows users to load a conversation by entering a conversation ID.
 * Provides an input field and button to load conversation history from the backend.
 * 
 * Features:
 * - Input field for conversation ID
 * - Load button to fetch conversation history
 * - Loading state indicator
 * - Error display if loading fails
 * - Clear button to reset the conversation
 */

'use client';

// React hooks for component state
import React, { useState } from 'react';
// Error trigger component for testing error boundary
import ErrorTrigger from './ErrorTrigger';

/**
 * Props interface for ConversationLoader component
 */
interface ConversationLoaderProps {
  // Function to call when loading a conversation
  onLoadConversation: (conversationId: string) => Promise<void>;
  // Whether a conversation is currently being loaded
  isLoading: boolean;
  // Current conversation ID (if any)
  currentConversationId: string | null;
  // Function to clear the current conversation
  onClearConversation: () => void;
}

/**
 * ConversationLoader component
 * 
 * Provides UI for loading conversations by conversation ID.
 * 
 * @param onLoadConversation - Function to call when user wants to load a conversation
 * @param isLoading - Whether a conversation is currently being loaded
 * @param currentConversationId - The current conversation ID (if any)
 * @param onClearConversation - Function to clear the current conversation
 */
export default function ConversationLoader({
  onLoadConversation,
  isLoading,
  currentConversationId,
  onClearConversation,
}: ConversationLoaderProps) {
  // State for the conversation ID input field
  const [conversationIdInput, setConversationIdInput] = useState('');

  /**
   * Handle loading a conversation
   * 
   * Validates the input and calls the onLoadConversation function.
   */
  const handleLoad = async () => {
    // Validate that conversation ID is provided
    if (!conversationIdInput.trim()) {
      alert('Please enter a conversation ID');
      return;
    }

    // Call the load conversation function
    await onLoadConversation(conversationIdInput.trim());
    // Clear input field after loading
    setConversationIdInput('');
  };

  /**
   * Handle clearing the current conversation
   * 
   * Clears the conversation ID from localStorage and resets the conversation.
   */
  const handleClear = () => {
    // Clear conversation ID from localStorage
    localStorage.removeItem('customer_support_conversation_id');
    // Call the clear conversation function
    onClearConversation();
    // Clear input field
    setConversationIdInput('');
  };

  return (
    <div className="bg-header border-b border-header-light p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 flex-wrap">
          {/* Conversation ID Input */}
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              value={conversationIdInput}
              onChange={(e) => setConversationIdInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !isLoading && conversationIdInput.trim()) {
                  handleLoad();
                }
              }}
              placeholder="Enter conversation ID to load..."
              disabled={isLoading}
              className="w-full px-4 py-2 bg-background border border-header-light rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:border-user disabled:opacity-50"
            />
          </div>

          {/* Load Button */}
          <button
            onClick={handleLoad}
            disabled={isLoading || !conversationIdInput.trim()}
            className="px-4 py-2 bg-agent hover:bg-agent-light rounded-lg text-agent-text transition-colors disabled:opacity-50 whitespace-nowrap"
          >
            {isLoading ? 'Loading...' : 'Load Conversation'}
          </button>

          {/* Clear Button - only show if there's a current conversation */}
          {currentConversationId && (
            <button
              onClick={handleClear}
              disabled={isLoading}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition-colors disabled:opacity-50 whitespace-nowrap"
            >
              Clear Conversation
            </button>
          )}

          {/* Current Conversation ID Display */}
          {currentConversationId && (
            <div className="text-sm text-text-secondary">
              <span className="font-semibold">Current:</span>{' '}
              <span className="font-mono text-xs">{currentConversationId}</span>
            </div>
          )}

          {/* Error Boundary Test Button */}
          {/* <div className="flex items-center gap-2">
            <span className="text-xs text-text-secondary">Test:</span>
            <ErrorTrigger />
          </div> */}
        </div>
      </div>
    </div>
  );
}
