/**
 * ComponentTests Component
 * 
 * Combined test page for MessageBubble and MessageInput components.
 * This page demonstrates both components working together in a chat-like interface.
 * 
 * Features:
 * - MessageBubble rendering with user and agent messages
 * - MessageInput functionality
 * - Interactive chat simulation
 * - All color palette verification
 */
'use client';

import React, { useState } from 'react';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import { Message } from '../types';

export default function ComponentTests() {
  // State to store messages
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      message: 'Hello! I\'m your AI assistant. How can I help you today?',
      sender: 'agent',
      timestamp: new Date(Date.now() - 60000).toISOString(),
    },
  ]);
  // State to simulate loading
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Handles sending a new message
   * 
   * @param messageText - The message text to send
   */
  const handleSend = (messageText: string) => {
    // Create user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      message: messageText,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    // Add user message
    setMessages((prev) => [...prev, userMessage]);

    // Simulate agent response
    setIsLoading(true);
    setTimeout(() => {
      const agentMessage: Message = {
        id: `agent-${Date.now()}`,
        message: `I received your message: "${messageText}". This is a test response from the agent.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, agentMessage]);
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="bg-header border-b border-header-light p-4">
        <h1 className="text-2xl font-bold text-header-text">
          Component Tests - MessageBubble & MessageInput
        </h1>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              sender={msg.sender}
              agentName="Support Agent"
            />
          ))}
          
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex items-start gap-3 mb-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-agent flex items-center justify-center">
                <span className="text-agent-text text-xs font-bold">A</span>
              </div>
              <div className="bg-agent rounded-lg px-4 py-2">
                <p className="text-agent-text text-sm">Agent is typing...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-header">
        <MessageInput
          onSend={handleSend}
          disabled={isLoading}
          placeholder="Message..."
          autoFocus={false}
        />
      </div>
    </div>
  );
}
