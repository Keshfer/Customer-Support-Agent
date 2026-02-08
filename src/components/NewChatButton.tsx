/**
 * NewChatButton Component
 * 
 * Component that provides a "New Chat" button to clear the current conversation.
 * The button is always visible but only performs an action if the conversation
 * has messages (is not empty).
 * 
 * Features:
 * - Always visible button
 * - Only clears conversation if it has messages
 * - Disabled during loading states
 * - Clears conversation ID from localStorage
 */

'use client';

// React hooks for component state
import React from 'react';
// Type definitions for messages
import { Message } from '@/types';

/**
 * Props interface for NewChatButton component
 */
interface NewChatButtonProps {
  // Function to clear the current conversation
  onClearConversation: () => void;
  // Whether a conversation is currently being loaded
  isLoading: boolean;
  // Array of messages in the current conversation
  messages: Message[];
}

/**
 * NewChatButton component
 * 
 * Provides a "New Chat" button that clears the current conversation.
 * The button only performs an action if the conversation has messages.
 * 
 * @param onClearConversation - Function to clear the current conversation
 * @param isLoading - Whether a conversation is currently being loaded
 * @param messages - Array of messages in the current conversation
 */
export default function NewChatButton({
  onClearConversation,
  isLoading,
  messages,
}: NewChatButtonProps) {
  /**
   * Handle clicking the New Chat button
   * 
   * Only clears the conversation if it has messages (is not empty).
   * Also clears the conversation ID from localStorage.
   */
  const handleNewChat = () => {
    // Only clear if conversation has messages
    if (messages.length === 0) {
      return;
    }

    // Clear conversation ID from localStorage
    localStorage.removeItem('customer_support_conversation_id');
    // Call the clear conversation function
    onClearConversation();
  };

  // Check if conversation is empty (no messages)
  const isEmpty = messages.length === 0;

  return (
    <button
      onClick={handleNewChat}
      disabled={isLoading || isEmpty}
      className={`
        px-4 py-1.5 rounded-t-lg text-sm font-medium whitespace-nowrap
        transition-colors duration-200
        ${isEmpty
          ? 'bg-header-light text-text-secondary opacity-50 cursor-not-allowed'
          : 'bg-header-light text-text-secondary hover:bg-header-light/80 hover:text-text-primary'
        }
        disabled:opacity-50
      `}
      title={isEmpty ? 'No conversation to clear' : 'Start a new chat'}
    >
      New Chat
    </button>
  );
}
