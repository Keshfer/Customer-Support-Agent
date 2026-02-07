/**
 * MessageList Component
 * 
 * Displays a scrollable list of chat messages with auto-scroll functionality.
 * 
 * Features:
 * - Renders list of messages using MessageBubble component
 * - Auto-scrolls to bottom when new messages are added
 * - Shows loading indicator when agent is generating a response
 * - Displays empty state when no messages are present
 * - Smooth scrolling behavior
 * 
 * @param {Message[]} props.messages - Array of message objects to display
 * @param {boolean} [props.isLoading] - Whether agent is currently generating a response
 * @param {string} [props.agentName] - Optional agent name to display in agent messages
 */
'use client';

import React, { useEffect, useRef } from 'react';
import { Message } from '../types';
import MessageBubble from './MessageBubble';

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  agentName?: string;
}

/**
 * MessageList component that renders a scrollable list of chat messages
 * 
 * @param messages - Array of messages to display
 * @param isLoading - Whether the agent is currently generating a response
 * @param agentName - Optional name for the agent (defaults to "AI Agent")
 */
export default function MessageList({ 
  messages, 
  isLoading = false,
  agentName = 'AI Agent'
}: MessageListProps) {
  // Ref to the scrollable container element
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // Ref to the messages container for scroll detection
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  /**
   * Scrolls to the bottom of the message list
   * Called automatically when messages change or when loading state changes
   */
  const scrollToBottom = () => {
    // Use smooth scrolling for better UX
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  /**
   * Effect hook that auto-scrolls to bottom when messages are added or loading state changes
   * This ensures new messages are always visible to the user
   */
  useEffect(() => {
    // Scroll to bottom whenever messages change or loading state changes
    scrollToBottom();
  }, [messages, isLoading]);

  /**
   * Renders the empty state when no messages are present
   * Shows a friendly message to encourage the user to start chatting
   */
  const renderEmptyState = () => {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-4">
        <div className="text-text-secondary text-lg mb-2">
          Welcome to Customer Support
        </div>
        <div className="text-text-muted text-sm">
          Start a conversation by sending a message below
        </div>
      </div>
    );
  };

  /**
   * Renders the loading indicator when agent is generating a response
   * Shows a typing animation to indicate the agent is working
   */
  const renderLoadingIndicator = () => {
    return (
      <div className="flex items-start gap-2 sm:gap-3 mb-4">
        {/* Agent avatar/logo */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-agent flex items-center justify-center">
          <span className="text-agent-text text-xs font-bold">A</span>
        </div>
        
        {/* Loading bubble */}
        <div className="flex flex-col max-w-[85%] sm:max-w-[70%] md:max-w-md min-w-0">
          {/* Agent name */}
          <div className="flex items-center gap-2 mb-1">
            <span className="text-text-primary text-sm font-semibold">{agentName}</span>
            <span className="text-text-secondary text-xs">•</span>
            <span className="text-text-secondary text-xs">AI Agent</span>
          </div>
          
          {/* Loading animation */}
          <div className="bg-agent rounded-lg px-3 py-2 sm:px-4 max-w-full overflow-hidden">
            <div className="flex gap-1">
              <span className="w-2 h-2 bg-agent-text rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
              <span className="w-2 h-2 bg-agent-text rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
              <span className="w-2 h-2 bg-agent-text rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Render empty state if no messages
  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 overflow-hidden flex flex-col">
        {renderEmptyState()}
      </div>
    );
  }

  // Render message list with scrollable container
  return (
    <div 
      ref={messagesContainerRef}
      className="flex-1 overflow-y-auto px-2 sm:px-4 py-4 sm:py-6"
    >
      {/* Messages container */}
      <div className="space-y-1">
        {/* Render each message using MessageBubble component */}
        {messages.map((message) => (
          <MessageBubble
            key={message.id || `${message.sender}-${message.timestamp}`}
            message={message}
            sender={message.sender}
            timestamp={message.timestamp}
            agentName={agentName}
          />
        ))}
        
        {/* Loading indicator when agent is generating response */}
        {isLoading && renderLoadingIndicator()}
        
        {/* Invisible element at the bottom for auto-scrolling */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
