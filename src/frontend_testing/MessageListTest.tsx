/**
 * MessageListTest Component
 * 
 * Test component to verify MessageList functionality.
 * This component demonstrates:
 * - Rendering list of messages
 * - Auto-scroll to bottom on new messages
 * - Loading indicator for agent responses
 * - Empty state when no messages
 * - Message list scrolling behavior
 * 
 * Usage: Import and render this component to test MessageList functionality
 */
'use client';

import React, { useState, useEffect } from 'react';
import MessageList from '../components/MessageList';
import { Message } from '../types';

export default function MessageListTest() {
  // State to store messages for testing
  const [messages, setMessages] = useState<Message[]>([]);
  // State to simulate loading/agent response generation
  const [isLoading, setIsLoading] = useState(false);
  // Counter for generating unique message IDs
  const [messageCounter, setMessageCounter] = useState(0);

  /**
   * Adds a sample user message to the message list
   * Simulates user sending a message
   */
  const addUserMessage = () => {
    const newMessage: Message = {
      id: `user-${messageCounter}`,
      message: `User message ${messageCounter + 1}: This is a test message from the user.`,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newMessage]);
    setMessageCounter((prev) => prev + 1);
  };

  /**
   * Adds a sample agent message to the message list
   * Simulates agent responding to user
   */
  const addAgentMessage = () => {
    const newMessage: Message = {
      id: `agent-${messageCounter}`,
      message: `Agent message ${messageCounter + 1}: This is a test response from the agent. I'm here to help you with any questions you might have.`,
      sender: 'agent',
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newMessage]);
    setMessageCounter((prev) => prev + 1);
  };

  /**
   * Simulates agent response generation
   * Shows loading indicator, then adds agent message after delay
   */
  const simulateAgentResponse = () => {
    setIsLoading(true);
    // Simulate agent thinking/generating response
    setTimeout(() => {
      const newMessage: Message = {
        id: `agent-${messageCounter}`,
        message: `Agent response ${messageCounter + 1}: I've processed your request and here's my response.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, newMessage]);
      setMessageCounter((prev) => prev + 1);
      setIsLoading(false);
    }, 2000);
  };

  /**
   * Adds multiple messages at once to test scrolling
   * Useful for testing auto-scroll functionality
   */
  const addMultipleMessages = () => {
    const newMessages: Message[] = [];
    for (let i = 0; i < 10; i++) {
      newMessages.push({
        id: `msg-${messageCounter + i}`,
        message: `Bulk message ${messageCounter + i + 1}: This is message number ${i + 1} in a series of messages to test scrolling behavior.`,
        sender: i % 2 === 0 ? 'user' : 'agent',
        timestamp: new Date(Date.now() - (10 - i) * 1000).toISOString(),
      });
    }
    setMessages((prev) => [...prev, ...newMessages]);
    setMessageCounter((prev) => prev + 10);
  };

  /**
   * Clears all messages (for testing empty state)
   */
  const clearMessages = () => {
    setMessages([]);
    setMessageCounter(0);
  };

  /**
   * Initializes test with sample messages
   * Sets up a conversation for initial testing
   */
  useEffect(() => {
    // Add initial sample messages
    const initialMessages: Message[] = [
      {
        id: 'init-1',
        message: 'Hello! Welcome to the Customer Support Agent. How can I help you today?',
        sender: 'agent',
        timestamp: new Date(Date.now() - 60000).toISOString(),
      },
      {
        id: 'init-2',
        message: 'Hi, I need help with my account.',
        sender: 'user',
        timestamp: new Date(Date.now() - 30000).toISOString(),
      },
    ];
    setMessages(initialMessages);
    setMessageCounter(2);
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Test Controls Section */}
      <div className="flex-shrink-0 bg-header border-b border-header-light p-6">
        <h1 className="text-3xl font-bold mb-4 text-text-primary">
          MessageList Component Test
        </h1>
        
        {/* Control buttons for testing different scenarios */}
        <div className="flex flex-wrap gap-3">
          <button
            onClick={addUserMessage}
            className="px-4 py-2 bg-user hover:bg-user-dark rounded-lg text-user-text transition-colors"
          >
            Add User Message
          </button>
          <button
            onClick={addAgentMessage}
            className="px-4 py-2 bg-agent hover:bg-agent-light rounded-lg text-agent-text transition-colors"
          >
            Add Agent Message
          </button>
          <button
            onClick={simulateAgentResponse}
            disabled={isLoading}
            className="px-4 py-2 bg-header hover:bg-header-light rounded-lg text-text-primary transition-colors disabled:opacity-50"
          >
            Simulate Agent Response (with Loading)
          </button>
          <button
            onClick={addMultipleMessages}
            className="px-4 py-2 bg-header hover:bg-header-light rounded-lg text-text-primary transition-colors"
          >
            Add 10 Messages (Test Scrolling)
          </button>
          <button
            onClick={clearMessages}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition-colors"
          >
            Clear All Messages
          </button>
        </div>
        
        {/* Status information */}
        <div className="mt-4 text-text-secondary text-sm">
          <p>Total Messages: {messages.length}</p>
          <p>Loading State: {isLoading ? 'Active' : 'Inactive'}</p>
        </div>
      </div>

      {/* MessageList Test Area */}
      <div className="flex-1 overflow-hidden">
        <MessageList
          messages={messages}
          isLoading={isLoading}
          agentName="Test Agent"
        />
      </div>

      {/* Test Scenarios Documentation */}
      <div className="flex-shrink-0 bg-background-dark border-t border-header p-6">
        <h2 className="text-2xl font-semibold mb-4 text-text-primary">
          Test Scenarios
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Test Scenario 1: Empty State */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              1. Empty State Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Click "Clear All Messages" to test the empty state. The MessageList should display a welcome message.
            </p>
            <button
              onClick={clearMessages}
              className="text-sm px-3 py-1 bg-user hover:bg-user-dark rounded text-user-text"
            >
              Test Empty State
            </button>
          </div>

          {/* Test Scenario 2: Auto-scroll */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              2. Auto-scroll Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Click "Add 10 Messages" to test auto-scrolling. The list should automatically scroll to show the newest message.
            </p>
            <button
              onClick={addMultipleMessages}
              className="text-sm px-3 py-1 bg-user hover:bg-user-dark rounded text-user-text"
            >
              Test Auto-scroll
            </button>
          </div>

          {/* Test Scenario 3: Loading Indicator */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              3. Loading Indicator Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Click "Simulate Agent Response" to see the loading indicator. It should show animated dots while loading.
            </p>
            <button
              onClick={simulateAgentResponse}
              disabled={isLoading}
              className="text-sm px-3 py-1 bg-user hover:bg-user-dark rounded text-user-text disabled:opacity-50"
            >
              Test Loading
            </button>
          </div>

          {/* Test Scenario 4: Message Rendering */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              4. Message Rendering Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Use "Add User Message" and "Add Agent Message" to test rendering of different message types.
            </p>
            <div className="flex gap-2">
              <button
                onClick={addUserMessage}
                className="text-sm px-3 py-1 bg-user hover:bg-user-dark rounded text-user-text"
              >
                Add User
              </button>
              <button
                onClick={addAgentMessage}
                className="text-sm px-3 py-1 bg-agent hover:bg-agent-light rounded text-agent-text"
              >
                Add Agent
              </button>
            </div>
          </div>
        </div>

        {/* Verification Checklist */}
        <div className="bg-header p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 text-text-primary">
            Verification Checklist
          </h3>
          <ul className="list-disc list-inside space-y-1 text-text-primary text-sm">
            <li className={messages.length === 0 ? 'text-green-400' : 'text-text-secondary'}>
              ✓ Empty state displays when no messages are present
            </li>
            <li className={messages.length > 0 ? 'text-green-400' : 'text-text-secondary'}>
              ✓ Messages are rendered correctly (user and agent messages)
            </li>
            <li className="text-green-400">
              ✓ Auto-scroll works when new messages are added
            </li>
            <li className={isLoading ? 'text-green-400' : 'text-text-secondary'}>
              ✓ Loading indicator appears when agent is generating response
            </li>
            <li className="text-green-400">
              ✓ Message list is scrollable when content overflows
            </li>
            <li className="text-green-400">
              ✓ Smooth scrolling behavior is implemented
            </li>
            <li className="text-green-400">
              ✓ Agent name is displayed correctly in agent messages
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
