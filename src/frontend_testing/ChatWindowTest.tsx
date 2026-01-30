/**
 * ChatWindowTest Component
 * 
 * Test component to verify ChatWindow functionality.
 * This component demonstrates:
 * - Main container for chat interface
 * - Header with title "Customer Support Agent"
 * - Message list area (scrollable)
 * - Message input area at bottom
 * - Integration of all chat components
 * - Layout matching finAI.png design
 * 
 * Usage: Import and render this component to test ChatWindow functionality
 */
'use client';

import React, { useState, useEffect } from 'react';
import ChatWindow from '../components/ChatWindow';
import { Message } from '../types';

export default function ChatWindowTest() {
  // State to store messages for the chat
  const [messages, setMessages] = useState<Message[]>([]);
  // State to simulate loading/agent response generation
  const [isLoading, setIsLoading] = useState(false);
  // Counter for generating unique message IDs
  const [messageCounter, setMessageCounter] = useState(0);

  /**
   * Handles message sending from ChatWindow
   * Simulates sending a user message and generating an agent response
   * 
   * @param messageText - The message text sent by the user
   */
  const handleSendMessage = (messageText: string) => {
    // Create user message object
    const userMessage: Message = {
      id: `user-${messageCounter}`,
      message: messageText,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };

    // Add user message to the message list
    setMessages((prev) => [...prev, userMessage]);
    setMessageCounter((prev) => prev + 1);

    // Simulate agent response generation
    setIsLoading(true);
    
    // Simulate agent thinking/generating response (with delay)
    setTimeout(() => {
      // Create agent response message
      const agentMessage: Message = {
        id: `agent-${messageCounter}`,
        message: `Thank you for your message: "${messageText}". This is a simulated agent response. I'm here to help you with any questions you might have.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
      };
      
      // Add agent message to the message list
      setMessages((prev) => [...prev, agentMessage]);
      setMessageCounter((prev) => prev + 1);
      
      // Stop loading state
      setIsLoading(false);
    }, 2000);
  };

  /**
   * Initializes test with sample conversation
   * Sets up initial messages to demonstrate the chat interface
   */
  useEffect(() => {
    // Add initial welcome messages
    const initialMessages: Message[] = [
      {
        id: 'init-1',
        message: 'Hello! Welcome to the Customer Support Agent. I\'m here to help you with any questions or issues you might have. How can I assist you today?',
        sender: 'agent',
        timestamp: new Date(Date.now() - 120000).toISOString(), // 2 minutes ago
      },
      {
        id: 'init-2',
        message: 'Hi, I need help with my account settings.',
        sender: 'user',
        timestamp: new Date(Date.now() - 60000).toISOString(), // 1 minute ago
      },
      {
        id: 'init-3',
        message: 'I\'d be happy to help you with your account settings! What specific aspect would you like to change or learn more about?',
        sender: 'agent',
        timestamp: new Date(Date.now() - 30000).toISOString(), // 30 seconds ago
      },
    ];
    
    setMessages(initialMessages);
    setMessageCounter(3);
  }, []);

  /**
   * Adds a sample user message programmatically
   * Useful for testing without typing
   */
  const addSampleUserMessage = () => {
    const sampleMessages = [
      'Can you help me reset my password?',
      'I want to update my email address',
      'How do I change my subscription plan?',
      'I\'m having trouble logging in',
      'What are your business hours?',
    ];
    const randomMessage = sampleMessages[Math.floor(Math.random() * sampleMessages.length)];
    handleSendMessage(randomMessage);
  };

  /**
   * Adds multiple messages to test scrolling
   * Useful for testing the message list with many messages
   */
  const addMultipleMessages = () => {
    const newMessages: Message[] = [];
    for (let i = 0; i < 5; i++) {
      newMessages.push({
        id: `msg-${messageCounter + i}`,
        message: `Test message ${i + 1}: This is a test message to verify scrolling and layout behavior.`,
        sender: i % 2 === 0 ? 'user' : 'agent',
        timestamp: new Date(Date.now() - (5 - i) * 1000).toISOString(),
      });
    }
    setMessages((prev) => [...prev, ...newMessages]);
    setMessageCounter((prev) => prev + 5);
  };

  /**
   * Clears all messages (for testing empty state)
   */
  const clearMessages = () => {
    setMessages([]);
    setMessageCounter(0);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Test Controls Panel - sits above ChatWindow header */}
      <div className="flex-shrink-0 bg-header border-b border-header-light p-4">
        <div className="flex items-center justify-between mb-3">
          <h1 className="text-2xl font-bold text-text-primary">
            ChatWindow Component Test
          </h1>
          <div className="text-text-secondary text-sm">
            Messages: {messages.length} | Loading: {isLoading ? 'Yes' : 'No'}
          </div>
        </div>
        {/* Control buttons for testing different scenarios */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={addSampleUserMessage}
            disabled={isLoading}
            className="px-3 py-1.5 bg-user hover:bg-user-dark rounded-lg text-user-text text-sm transition-colors disabled:opacity-50"
          >
            Add Sample Message
          </button>
          <button
            onClick={addMultipleMessages}
            className="px-3 py-1.5 bg-header-light hover:bg-header rounded-lg text-text-primary text-sm transition-colors"
          >
            Add 5 Test Messages
          </button>
          <button
            onClick={clearMessages}
            className="px-3 py-1.5 bg-red-600 hover:bg-red-700 rounded-lg text-white text-sm transition-colors"
          >
            Clear All
          </button>
        </div>
      </div>

      {/* ChatWindow Component Test Area - takes remaining space, allows scrolling */}
      <div className="flex-1 overflow-hidden min-h-0 flex flex-col">
        <ChatWindow
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          agentName="Support Agent"
        />
      </div>

      {/* Test Documentation Panel (collapsible) */}
      <div className="flex-shrink-0 bg-background-dark border-t border-header p-4 max-h-64 overflow-y-auto">
        <details className="cursor-pointer">
          <summary className="text-lg font-semibold text-text-primary mb-2">
            Test Scenarios & Verification Checklist
          </summary>
          
          <div className="mt-3 space-y-4">
            {/* Test Scenarios */}
            <div>
              <h3 className="text-md font-semibold text-text-primary mb-2">
                Test Scenarios:
              </h3>
              <ul className="list-disc list-inside space-y-1 text-text-secondary text-sm ml-2">
                <li>
                  <strong>Basic Chat Flow:</strong> Type a message in the input field and press Enter or click send. Verify the message appears and agent responds.
                </li>
                <li>
                  <strong>Empty State:</strong> Click "Clear All" to test the empty state display.
                </li>
                <li>
                  <strong>Scrolling:</strong> Click "Add 5 Test Messages" to test scrolling behavior with many messages.
                </li>
                <li>
                  <strong>Loading State:</strong> Send a message and observe the loading indicator while agent generates response.
                </li>
                <li>
                  <strong>Layout:</strong> Verify header, message area, and input area are properly positioned.
                </li>
              </ul>
            </div>

            {/* Verification Checklist */}
            <div>
              <h3 className="text-md font-semibold text-text-primary mb-2">
                Verification Checklist:
              </h3>
              <ul className="list-disc list-inside space-y-1 text-text-primary text-sm ml-2">
                <li className={messages.length === 0 ? 'text-green-400' : 'text-text-secondary'}>
                  ✓ Empty state displays when no messages (after clearing)
                </li>
                <li className={messages.length > 0 ? 'text-green-400' : 'text-text-secondary'}>
                  ✓ Header displays "Customer Support Agent" title
                </li>
                <li className="text-green-400">
                  ✓ Message list area is scrollable
                </li>
                <li className="text-green-400">
                  ✓ Message input area is at the bottom
                </li>
                <li className="text-green-400">
                  ✓ Input field has placeholder "Input text here"
                </li>
                <li className="text-green-400">
                  ✓ Send button has upward arrow icon
                </li>
                <li className={isLoading ? 'text-green-400' : 'text-text-secondary'}>
                  ✓ Loading indicator appears when agent is responding
                </li>
                <li className="text-green-400">
                  ✓ Input is disabled during loading
                </li>
                <li className="text-green-400">
                  ✓ Messages are sent and displayed correctly
                </li>
                <li className="text-green-400">
                  ✓ Layout matches dark theme design
                </li>
                <li className="text-green-400">
                  ✓ All components are properly integrated
                </li>
              </ul>
            </div>
          </div>
        </details>
      </div>
    </div>
  );
}
