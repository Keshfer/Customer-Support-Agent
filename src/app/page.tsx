/**
 * Home Page
 * 
 * Main page component that renders the ChatWindow with full chat functionality.
 * 
 * Features:
 * - Integrates useChat hook for state management
 * - Renders ChatWindow component
 * - ConversationLoader component for loading conversations by ID
 * - Auto-loads conversation from localStorage on page load
 * - Error boundary for error handling
 * - Clear conversation functionality
 */
'use client';

// React hooks for component state and effects
import { useEffect, useRef } from 'react';
// Custom hook for chat functionality
import { useChat } from '@/hooks/useChat';
// Chat interface component
import ChatWindow from '@/components/ChatWindow';
// Component for loading conversations by ID
import ConversationLoader from '@/components/ConversationLoader';
// Component for displaying conversation tabs
import ConversationTabs from '@/components/ConversationTabs';
// Error boundary component for catching errors
import ErrorBoundary from '@/components/ErrorBoundary';

/**
 * Main page component
 * 
 * Renders the chat interface with full functionality including:
 * - Chat window for displaying messages
 * - Conversation loader for loading previous conversations
 * - Auto-loading conversation from localStorage
 * - Error boundary for error handling
 */
export default function Home() {
  // Use the useChat hook to manage chat state and functionality
  const {
    messages,
    conversationId,
    isLoading,
    error,
    sendMessage,
    loadConversation,
    clearError,
    clearConversation,
  } = useChat();

  // Ref to track if we've already attempted to auto-load conversation
  // This prevents multiple load attempts
  const hasAttemptedAutoLoad = useRef(false);

  /**
   * Auto-load conversation from localStorage on page load
   * 
   * If a conversation ID exists in localStorage, automatically load
   * the conversation history when the conversationId is set from localStorage.
   * This effect watches conversationId and loads messages when it's first set.
   */
  useEffect(() => {
    // If conversationId exists, we don't have messages yet, we're not loading, and we haven't attempted to load yet
    if (conversationId && messages.length === 0 && !isLoading && !hasAttemptedAutoLoad.current) {
      // Mark that we've attempted to load
      hasAttemptedAutoLoad.current = true;
      
      // Load the conversation history from the backend
      loadConversation(conversationId).catch((err) => {
        // If loading fails, log the error but don't block the UI
        // The user can still start a new conversation
        console.error('Failed to auto-load conversation:', err);
        // Reset the flag so user can try again manually
        hasAttemptedAutoLoad.current = false;
      });
    }
    
    // Reset the flag if conversationId is cleared (allows re-loading if user clears and starts new)
    if (!conversationId) {
      hasAttemptedAutoLoad.current = false;
    }
  }, [conversationId, messages.length, isLoading, loadConversation]); // Dependencies: watch for conversationId, messages, and loading state

  /**
   * Handle clearing the current conversation
   * 
   * Clears the conversation ID from localStorage and resets the chat state.
   * Uses the clearConversation function from useChat hook to clear all state.
   */
  const handleClearConversation = () => {
    // Clear conversation ID from localStorage
    localStorage.removeItem('customer_support_conversation_id');
    // Clear conversation using hook function (clears messages, conversationId, and errors)
    clearConversation();
  };

  /**
   * Handle sending a message
   * 
   * Wrapper function that calls sendMessage from useChat hook.
   * This allows us to pass it directly to ChatWindow component.
   * 
   * @param message - The message text to send
   */
  const handleSendMessage = (message: string) => {
    // Call sendMessage from useChat hook
    sendMessage(message);
  };

  /**
   * Handle clicking on a conversation tab
   * 
   * Loads the conversation history for the clicked conversation.
   * This function is passed to ConversationTabs component.
   * 
   * @param conversationId - The ID of the conversation to load
   */
  const handleConversationClick = (conversationId: string) => {
    // Load the conversation using the loadConversation function from useChat hook
    loadConversation(conversationId).catch((err) => {
      // If loading fails, log the error
      // The error will be displayed via the error state
      console.error('Failed to load conversation:', err);
    });
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background flex flex-col">
        {/* Conversation Tabs Component */}
        <ConversationTabs
          currentConversationId={conversationId}
          onConversationClick={handleConversationClick}
          isLoading={isLoading}
        />

        {/* Conversation Loader Component */}
        <ConversationLoader
          onLoadConversation={loadConversation}
          isLoading={isLoading}
          currentConversationId={conversationId}
          onClearConversation={handleClearConversation}
        />

        {/* Chat Window Component */}
        <div className="flex-1 overflow-hidden">
          <ChatWindow
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            agentName="Customer Support Agent"
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className="fixed bottom-4 right-4 bg-red-600 p-4 rounded-lg shadow-lg max-w-md z-50">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-white">Error:</p>
                <p className="text-red-100">{error.message}</p>
              </div>
              <button
                onClick={clearError}
                className="ml-4 text-white hover:text-red-200 text-xl"
                aria-label="Close error"
              >
                ×
              </button>
            </div>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
}
