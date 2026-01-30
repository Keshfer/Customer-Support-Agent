/**
 * ChatWindow Component
 * 
 * Main container component for the chat interface that orchestrates all chat-related components.
 * 
 * Features:
 * - Header with title "Customer Support Agent"
 * - Scrollable message list area
 * - Message input area at the bottom
 * - Layout matching finAI.png design (dark theme)
 * - Integrates MessageList and MessageInput components
 * 
 * @param {Message[]} props.messages - Array of messages to display in the chat
 * @param {Function} props.onSendMessage - Callback function called when user sends a message
 * @param {boolean} [props.isLoading] - Whether agent is currently generating a response
 * @param {string} [props.agentName] - Optional agent name to display
 */
'use client';

import React from 'react';
import { Message } from '../types';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

interface ChatWindowProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  agentName?: string;
}

/**
 * ChatWindow component that serves as the main container for the chat interface
 * 
 * @param messages - Array of messages to display
 * @param onSendMessage - Callback function when user sends a message
 * @param isLoading - Whether the agent is currently generating a response
 * @param agentName - Optional name for the agent (defaults to "AI Agent")
 */
export default function ChatWindow({
  messages,
  onSendMessage,
  isLoading = false,
  agentName = 'AI Agent',
}: ChatWindowProps) {
  /**
   * Handles message sending from MessageInput component
   * Forwards the message to the parent component via onSendMessage callback
   * 
   * @param message - The message text to send
   */
  const handleSendMessage = (message: string) => {
    onSendMessage(message);
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header section with title */}
      <header className="flex-shrink-0 bg-header border-b border-header-light px-6 py-4">
        <div className="flex items-center">
          {/* Header title */}
          <h1 className="text-text-primary text-xl font-semibold">
            Customer Support Agent
          </h1>
          
          {/* Future: Navigation controls can be added here */}
          {/* - Back arrow icon */}
          {/* - Menu dots icon */}
          {/* - Expand/fullscreen icon */}
        </div>
      </header>

      {/* Message list area - scrollable container */}
      {/* This div must be a flex container for MessageList's flex-1 to work */}
      <div className="flex-1 overflow-hidden min-h-0 flex flex-col">
        <MessageList
          messages={messages}
          isLoading={isLoading}
          agentName={agentName}
        />
      </div>

      {/* Message input area at the bottom */}
      <div className="flex-shrink-0">
        <MessageInput
          onSend={handleSendMessage}
          disabled={isLoading}
          placeholder="Input text here"
          autoFocus={true}
        />
      </div>
    </div>
  );
}
