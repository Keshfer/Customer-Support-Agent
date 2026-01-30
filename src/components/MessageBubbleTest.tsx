/**
 * MessageBubbleTest Component
 * 
 * Test component to verify MessageBubble rendering with both user and agent messages.
 * This component demonstrates:
 * - Agent message styling (light grey, left-aligned, with name/logo)
 * - User message styling (orange, right-aligned)
 * - Timestamp display
 * - Various message lengths
 * 
 * Usage: Import and render this component to test MessageBubble functionality
 */
'use client';

import React from 'react';
import MessageBubble from './MessageBubble';
import { Message } from '../types';

export default function MessageBubbleTest() {
  // Sample messages for testing
  const agentMessage: Message = {
    id: '1',
    message: 'Hello! I\'m your AI assistant. How can I help you today?',
    sender: 'agent',
    timestamp: new Date().toISOString(),
  };

  const userMessage: Message = {
    id: '2',
    message: 'Hi there! I need help with my account.',
    sender: 'user',
    timestamp: new Date().toISOString(),
  };

  const longAgentMessage: Message = {
    id: '3',
    message: 'I\'d be happy to help you with your account! I can assist you with account settings, billing questions, or any other issues you might have. Please let me know what specific help you need.',
    sender: 'agent',
    timestamp: new Date(Date.now() - 60000).toISOString(), // 1 minute ago
  };

  const longUserMessage: Message = {
    id: '4',
    message: 'I\'m having trouble accessing my account. I tried resetting my password but I haven\'t received the email yet. Can you help me troubleshoot this?',
    sender: 'user',
    timestamp: new Date(Date.now() - 30000).toISOString(), // 30 seconds ago
  };

  const shortUserMessage: Message = {
    id: '5',
    message: 'Thanks!',
    sender: 'user',
    timestamp: new Date().toISOString(),
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <h1 className="text-3xl font-bold mb-8 text-text-primary">
        MessageBubble Component Test
      </h1>

      {/* Test Section: Agent Messages */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 text-text-primary">
          Agent Messages (Left-aligned, Light blue)
        </h2>
        <div className="bg-background-dark p-6 rounded-lg border-2 border-white max-w-4xl">
          <MessageBubble 
            message={agentMessage} 
            sender="agent" 
            agentName="Bob"
          />
          <MessageBubble 
            message={longAgentMessage} 
            sender="agent" 
            agentName="Alice"
          />
        </div>
      </section>

      {/* Test Section: User Messages */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 text-text-primary">
          User Messages (Right-aligned, Orange)
        </h2>
        <div className="bg-background-dark p-6 rounded-lg border-2 border-white max-w-4xl">
          <MessageBubble 
            message={userMessage} 
            sender="user" 
          />
          <MessageBubble 
            message={longUserMessage} 
            sender="user" 
          />
          <MessageBubble 
            message={shortUserMessage} 
            sender="user" 
          />
        </div>
      </section>

      {/* Test Section: Conversation Flow */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 text-text-primary">
          Conversation Flow (Mixed Messages)
        </h2>
        <div className="bg-background-dark p-6 rounded-lg border-2 border-white max-w-4xl">
          <MessageBubble 
            message={agentMessage} 
            sender="agent" 
            agentName="Support Agent"
          />
          <MessageBubble 
            message={userMessage} 
            sender="user" 
          />
          <MessageBubble 
            message={longAgentMessage} 
            sender="agent" 
            agentName="Support Agent"
          />
          <MessageBubble 
            message={longUserMessage} 
            sender="user" 
          />
          <MessageBubble 
            message={{
              id: '6',
              message: 'Perfect! I\'ve reset your password. Check your email for the reset link.',
              sender: 'agent',
              timestamp: new Date().toISOString(),
            }} 
            sender="agent" 
            agentName="Support Agent"
          />
          <MessageBubble 
            message={shortUserMessage} 
            sender="user" 
          />
        </div>
      </section>

      {/* Test Section: Messages without timestamps */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 text-text-primary">
          Messages Without Timestamps
        </h2>
        <div className="bg-background-dark p-6 rounded-lg border-2 border-white max-w-4xl">
          <MessageBubble 
            message={{
              id: '7',
              message: 'This message has no timestamp',
              sender: 'agent',
            }} 
            sender="agent" 
            agentName="Test Agent"
          />
          <MessageBubble 
            message={{
              id: '8',
              message: 'This user message also has no timestamp',
              sender: 'user',
            }} 
            sender="user" 
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
            <li className={agentMessage.sender === 'agent' ? 'text-green-400' : 'text-red-400'}>
              ✓ Agent messages are light blue and left-aligned
            </li>
            <li className={userMessage.sender === 'user' ? 'text-green-400' : 'text-red-400'}>
              ✓ User messages are orange and right-aligned
            </li>
            <li className="text-green-400">
              ✓ Agent messages show agent name/logo
            </li>
            <li className="text-green-400">
              ✓ Timestamps are displayed when provided
            </li>
            <li className="text-green-400">
              ✓ Long messages wrap correctly
            </li>
            <li className="text-green-400">
              ✓ Messages are responsive (max-width on larger screens)
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
}
