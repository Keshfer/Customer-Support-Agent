/**
 * MessageBubble Component
 * 
 * Displays a single chat message bubble with conditional styling based on sender.
 * 
 * Features:
 * - Agent messages: Light blue bubble, left-aligned, with agent name/logo
 * - User messages: Orange rounded rectangle, right-aligned
 * - Timestamp display for each message
 * - Responsive design
 * 
 * @param {Message} props.message - The message object containing content and metadata
 * @param {'user' | 'agent'} props.sender - The sender type (user or agent)
 * @param {string} [props.timestamp] - Optional timestamp to display
 * @param {string} [props.agentName] - Optional agent name to display (defaults to "AI Agent")
 */
import React from 'react';
import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
  sender: 'user' | 'agent';
  timestamp?: string;
  agentName?: string;
}

/**
 * Formats a timestamp string to a readable time format
 * 
 * @param timestamp - ISO timestamp string or date string
 * @returns Formatted time string (e.g., "10:30 AM")
 */
const formatTimestamp = (timestamp?: string): string => {
  if (!timestamp) return '';
  
  try {
    const date = new Date(timestamp);
    // Format as HH:MM AM/PM
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  } catch (error) {
    // Return original timestamp if parsing fails
    return timestamp;
  }
};

export default function MessageBubble({ 
  message, 
  sender, 
  timestamp, 
  agentName = 'AI Agent' 
}: MessageBubbleProps) {
  // Use timestamp from message if not provided as prop
  const displayTimestamp = timestamp || message.timestamp || '';
  const formattedTime = formatTimestamp(displayTimestamp);

  // Render agent message (left-aligned, light blue)
  if (sender === 'agent') {
    return (
      <div className="flex items-start gap-3 mb-4">
        {/* Agent avatar/logo */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-agent flex items-center justify-center">
          <span className="text-agent-text text-xs font-bold">A</span>
        </div>
        
        {/* Agent message bubble */}
        <div className="flex flex-col max-w-[70%] md:max-w-md min-w-0">
          {/* Agent name */}
          <div className="flex items-center gap-2 mb-1">
            <span className="text-text-primary text-sm font-semibold">{agentName}</span>
            <span className="text-text-secondary text-xs">•</span>
            <span className="text-text-secondary text-xs">AI Agent</span>
          </div>
          
          {/* Message content */}
          <div className="bg-agent rounded-lg px-4 py-2 max-x-full">
            <p className="text-agent-text text-sm whitespace-pre-wrap break-words">
              {message.message}
            </p>
          </div>
          
          {/* Timestamp */}
          {formattedTime && (
            <p className="text-text-muted text-xs mt-1 ml-1">
              {formattedTime}
            </p>
          )}
        </div>
      </div>
    );
  }

  // Render user message (right-aligned, orange)
  return (
    <div className="flex items-start gap-3 mb-4 justify-end">
      {/* User message bubble */}
      <div className="flex flex-col items-end max-w-[70%] md:max-w-md min-w-0">
        {/* Message content */}
        <div className="bg-user rounded-lg px-4 py-2 max-w-full">
          <p className="text-user-text text-sm whitespace-pre-wrap break-words">
            {message.message}
          </p>
        </div>
        
        {/* Timestamp */}
        {formattedTime && (
          <p className="text-text-muted text-xs mt-1 mr-1">
            {formattedTime}
          </p>
        )}
      </div>
    </div>
  );
}
