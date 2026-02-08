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
import { getAllConversations } from '@/lib/api';

interface Conversation {
  conversation_id: string;
  timestamp: string | null;
  first_message: string;
}

interface ConversationTabsProps {
  currentConversationId: string | null;
  onConversationClick: (conversationId: string) => void;
  isLoading?: boolean;
}

/**
 * ConversationTabs component that displays tabs for all conversations
 * 
 * @param currentConversationId - The ID of the currently active conversation
 * @param onConversationClick - Callback function when a conversation tab is clicked
 * @param isLoading - Whether conversations are being loaded
 */
export default function ConversationTabs({
  currentConversationId,
  onConversationClick,
  isLoading = false,
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

  // Don't render if there are no conversations and not loading
  if (!isFetching && conversations.length === 0 && !error) {
    return null;
  }

  return (
    <div className="w-full bg-header border-b border-header-light overflow-x-auto">
      <div className="flex items-center gap-2 px-4 py-2 min-w-max">
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
            <button
              key={conversation.conversation_id}
              onClick={() => handleTabClick(conversation.conversation_id)}
              className={`
                px-3 py-1.5 rounded-t-lg text-sm font-medium whitespace-nowrap
                transition-colors duration-200
                ${isActive
                  ? 'bg-background text-text-primary border-t-2 border-l-2 border-r-2 border-header-light'
                  : 'bg-header-light text-text-secondary hover:bg-header-light/80 hover:text-text-primary'
                }
              `}
              title={conversation.first_message || 'New Conversation'}
            >
              {displayText}
            </button>
          );
        })}
      </div>
    </div>
  );
}
