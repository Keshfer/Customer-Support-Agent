/**
 * MessageInputTest Component
 * 
 * Test component to verify MessageInput functionality.
 * This component demonstrates:
 * - Input field with placeholder
 * - Send button functionality
 * - Enter key to send
 * - Disabled state during loading
 * - Message sending callback
 * - Input validation (non-empty messages)
 * 
 * Usage: Import and render this component to test MessageInput functionality
 */
'use client';

import React, { useState } from 'react';
import MessageInput from './MessageInput';
import MessageBubble from './MessageBubble';
import { Message } from '../types';

export default function MessageInputTest() {
  // State to store sent messages for display
  const [messages, setMessages] = useState<Message[]>([]);
  // State to simulate loading/disabled state
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Handles message sending
   * Simulates sending a message and adding it to the message list
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

    // Add user message to list
    setMessages((prev) => [...prev, userMessage]);

    // Simulate agent response after a delay
    setIsLoading(true);
    setTimeout(() => {
      const agentMessage: Message = {
        id: `agent-${Date.now()}`,
        message: `You said: "${messageText}". This is a simulated agent response.`,
        sender: 'agent',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, agentMessage]);
      setIsLoading(false);
    }, 1500);
  };

  /**
   * Clears all messages (for testing)
   */
  const handleClear = () => {
    setMessages([]);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <div className="flex-1 overflow-y-auto p-8">
        <h1 className="text-3xl font-bold mb-8 text-text-primary">
          MessageInput Component Test
        </h1>

        {/* Test Section: Basic Functionality */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-text-primary">
            Basic Functionality Test
          </h2>
          <div className="bg-background-dark p-6 rounded-lg border-2 border-white max-w-4xl mb-4">
            <p className="text-text-secondary mb-4">
              Type a message and press Enter or click the send button. 
              The message will appear above, and a simulated agent response will follow.
            </p>
            
            {/* Display sent messages */}
            <div className="space-y-4 mb-4 min-h-[200px]">
              {messages.length === 0 ? (
                <p className="text-text-muted text-center py-8">
                  No messages yet. Send a message to test!
                </p>
              ) : (
                messages.map((msg) => (
                  <MessageBubble
                    key={msg.id}
                    message={msg}
                    sender={msg.sender}
                    agentName="Test Agent"
                  />
                ))
              )}
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
        </section>

        {/* Test Section: Disabled State */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-text-primary">
            Disabled State Test
          </h2>
          <div className="bg-background-dark p-6 rounded-lg border-2 border-white max-w-4xl">
            <p className="text-text-secondary mb-4">
              This input is always disabled to demonstrate the disabled state.
            </p>
            <MessageInput
              onSend={handleSend}
              disabled={true}
              placeholder="This input is disabled..."
            />
          </div>
        </section>

        {/* Test Section: Enabled State */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-text-primary">
            Enabled State Test (Interactive)
          </h2>
          <div className="bg-background-dark p-6 rounded-lg border-2 border-white max-w-4xl">
            <p className="text-text-secondary mb-4">
              This input is enabled and interactive. Try sending a message!
            </p>
            <MessageInput
              onSend={handleSend}
              disabled={isLoading}
              placeholder="Type your message here..."
              autoFocus={false}
            />
          </div>
        </section>

        {/* Verification Checklist */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold mb-4 text-text-primary">
            Verification Checklist
          </h2>
          <div className="bg-background-dark p-6 rounded-lg border-2 border-white max-w-4xl">
            <ul className="list-disc list-inside space-y-2 text-text-primary">
              <li className="text-green-400">
                ✓ Input field accepts text input
              </li>
              <li className="text-green-400">
                ✓ Placeholder text is displayed when input is empty
              </li>
              <li className="text-green-400">
                ✓ Send button has upward arrow icon in white circle
              </li>
              <li className="text-green-400">
                ✓ Enter key sends the message
              </li>
              <li className="text-green-400">
                ✓ Send button is disabled when input is empty
              </li>
              <li className="text-green-400">
                ✓ Input and button are disabled during loading/agent response
              </li>
              <li className="text-green-400">
                ✓ Input clears after sending a message
              </li>
              <li className="text-green-400">
                ✓ Empty messages (whitespace only) are not sent
              </li>
            </ul>
          </div>
        </section>

        {/* Control Buttons */}
        <section className="mb-12">
          <div className="bg-background-dark p-6 rounded-lg border-2 border-white max-w-4xl">
            <button
              onClick={handleClear}
              className="px-4 py-2 bg-header hover:bg-header-light rounded-lg text-text-primary transition-colors"
            >
              Clear Messages
            </button>
          </div>
        </section>
      </div>

      {/* Fixed Input at Bottom (Simulating Chat Interface) */}
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
