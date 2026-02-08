/**
 * ConversationTabs Component
 * 
 * Displays conversation tabs at the top of the page that users can click on
 * to switch between conversations. Each tab shows the first message sent in that conversation.
 * 
 * Features:
 * - Fetches all conversations on mount
 * - Displays tabs with first message as title
 * - Highlights the active conversation
 * - Handles tab clicks to switch conversations
 * - Prevents reloading if clicking the currently active conversation
 * - Responsive design for mobile devices
 * 
 * @param {string | null} props.currentConversationId - The ID of the currently active conversation
 * @param {Function} props.onConversationClick - Callback function when a conversation tab is clicked
 * @param {boolean} [props.isLoading] - Whether conversations are being loaded
 */

'use client';

import React, { useEffect, useState } from 'react';
import { getAllConversations, deleteConversation } from '@/lib/api';
import NewChatButton from './NewChatButton';
import { Message } from '@/types';

interface Conversation {
  conversation_id: string;
  timestamp: string | null;
  first_message: string;
}

interface ConversationTabsProps {
  currentConversationId: string | null;
  onConversationClick: (conversationId: string) => void;
  isLoading?: boolean;
  // Function to clear the current conversation
  onClearConversation: () => void;
  // Array of messages in the current conversation
  messages: Message[];
}

/**
 * ConversationTabs component that displays tabs for all conversations
 * 
 * @param currentConversationId - The ID of the currently active conversation
 * @param onConversationClick - Callback function when a conversation tab is clicked
 * @param isLoading - Whether conversations are being loaded
 * @param onClearConversation - Function to clear the current conversation
 * @param messages - Array of messages in the current conversation
 */
export default function ConversationTabs({
  currentConversationId,
  onConversationClick,
  isLoading = false,
  onClearConversation,
  messages,
}: ConversationTabsProps) {
  // State for storing all conversations
  const [conversations, setConversations] = useState<Conversation[]>([]);
  // State for tracking if conversations are being fetched
  const [isFetching, setIsFetching] = useState<boolean>(false);
  // State for storing any errors that occur
  const [error, setError] = useState<Error | null>(null);

  /**
   * Fetch all conversations from the backend
   * Called on component mount and when currentConversationId changes
   */
  useEffect(() => {
    const fetchConversations = async () => {
      setIsFetching(true);
      setError(null);
      
      try {
        const response = await getAllConversations();
        setConversations(response.conversations);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to fetch conversations');
        setError(error);
        console.error('Error fetching conversations:', error);
      } finally {
        setIsFetching(false);
      }
    };

    fetchConversations();
  }, [currentConversationId]); // Refetch when conversation changes to update list

  /**
   * Handle clicking on a conversation tab
   * Prevents reloading if clicking the currently active conversation
   * 
   * @param conversationId - The ID of the conversation to switch to
   */
  const handleTabClick = (conversationId: string) => {
    // Don't reload if clicking the currently active conversation
    if (conversationId === currentConversationId) {
      return;
    }
    
    // Call the callback to switch conversations
    onConversationClick(conversationId);
  };

  /**
   * Handle deleting a conversation
   * 
   * Deletes the conversation and switches to the conversation to the left
   * if the deleted conversation was the active one.
   * 
   * @param conversationIdToDelete - The ID of the conversation to delete
   * @param event - The click event to prevent propagation
   */
  const handleDeleteConversation = async (
    conversationIdToDelete: string,
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    // Prevent the tab click from firing
    event.stopPropagation();

    try {
      // Delete the conversation from the backend
      await deleteConversation(conversationIdToDelete);

      // Find the index of the deleted conversation
      const deletedIndex = conversations.findIndex(
        (conv) => conv.conversation_id === conversationIdToDelete
      );

      // Remove the conversation from the local state
      const updatedConversations = conversations.filter(
        (conv) => conv.conversation_id !== conversationIdToDelete
      );
      setConversations(updatedConversations);

      // If the deleted conversation was the active one, switch to the conversation to the left
      if (conversationIdToDelete === currentConversationId) {
        // Find the conversation to the left (previous index)
        if (deletedIndex > 0 && updatedConversations.length > 0) {
          // Switch to the conversation that was to the left
          const conversationToLeft = updatedConversations[deletedIndex - 1];
          if (conversationToLeft) {
            onConversationClick(conversationToLeft.conversation_id);
          }
        } else if (updatedConversations.length > 0) {
          // If we deleted the first conversation, switch to the new first one
          onConversationClick(updatedConversations[0].conversation_id);
        } else {
          // No conversations left, clear the current conversation
          onClearConversation();
        }
      }
    } catch (err) {
      // Handle error (could show a toast notification)
      const error = err instanceof Error ? err : new Error('Failed to delete conversation');
      console.error('Error deleting conversation:', error);
      setError(error);
    }
  };

  /**
   * Truncate message text for display in tabs
   * Limits the length to prevent tabs from being too wide
   * 
   * @param text - The text to truncate
   * @param maxLength - Maximum length before truncation (default: 50)
   * @returns Truncated text with ellipsis if needed
   */
  const truncateMessage = (text: string, maxLength: number = 50): string => {
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength) + '...';
  };

  // Always render to show New Chat button, even if no conversations exist
  return (
    <div className="w-full bg-header border-b border-header-light overflow-x-auto">
      <div className="flex items-center gap-2 px-4 py-2 min-w-max">
        {/* New Chat Button - always on the left */}
        <NewChatButton
          onClearConversation={onClearConversation}
          isLoading={isLoading}
          messages={messages}
        />

        {/* Loading indicator */}
        {isFetching && (
          <div className="text-text-secondary text-sm px-3 py-1.5">
            Loading conversations...
          </div>
        )}
        
        {/* Error message */}
        {error && !isFetching && (
          <div className="text-red-400 text-sm px-3 py-1.5">
            Failed to load conversations
          </div>
        )}
        
        {/* Conversation tabs */}
        {!isFetching && conversations.map((conversation) => {
          const isActive = conversation.conversation_id === currentConversationId;
          const displayText = conversation.first_message 
            ? truncateMessage(conversation.first_message)
            : 'New Conversation';
          
          return (
            <div
              key={conversation.conversation_id}
              className={`
                flex items-center gap-1 rounded-t-lg
                transition-colors duration-200
                ${isActive
                  ? 'bg-background border-t-2 border-l-2 border-r-2 border-header-light'
                  : 'bg-header-light'
                }
              `}
            >
              <button
                onClick={() => handleTabClick(conversation.conversation_id)}
                className={`
                  px-3 py-1.5 text-sm font-medium whitespace-nowrap
                  transition-colors duration-200
                  ${isActive
                    ? 'text-text-primary'
                    : 'text-text-secondary hover:bg-header-light/80 hover:text-text-primary'
                  }
                `}
                title={conversation.first_message || 'New Conversation'}
              >
                {displayText}
              </button>
              <button
                onClick={(e) => handleDeleteConversation(conversation.conversation_id, e)}
                disabled={isLoading}
                className={`
                  px-2 py-1.5 text-xs font-bold rounded-t-lg
                  transition-colors duration-200
                  ${isActive
                    ? 'text-text-secondary hover:text-text-primary hover:bg-background/50'
                    : 'text-text-secondary hover:text-text-primary hover:bg-header-light/80'
                  }
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
                title="Delete conversation"
                aria-label="Delete conversation"
              >
                ×
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
