/**
 * MessageInput Component
 * 
 * Input component for sending messages in the chat interface.
 * 
 * Features:
 * - Text input field with placeholder
 * - Send button with upward arrow icon in white circle
 * - Enter key to send message
 * - Disabled state during loading and when agent is generating response
 * - Auto-focus on mount (optional)
 * - Input validation (non-empty messages)
 * 
 * @param {Function} props.onSend - Callback function called when message is sent
 * @param {boolean} [props.disabled] - Whether input is disabled (during loading/agent response)
 * @param {string} [props.placeholder] - Placeholder text for input (default: "Message...")
 * @param {boolean} [props.autoFocus] - Whether to auto-focus input on mount
 */
'use client';

import React, { useState, useRef, useEffect } from 'react';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  autoFocus?: boolean;
}

export default function MessageInput({
  onSend,
  disabled = false,
  placeholder = 'Message...',
  autoFocus = false,
}: MessageInputProps) {
  // State for input value
  const [inputValue, setInputValue] = useState('');
  // Ref for input element (for auto-focus)
  const inputRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Auto-focus input on mount if autoFocus prop is true
   */
  useEffect(() => {
    if (autoFocus && inputRef.current) {
      inputRef.current.focus();
    }
  }, [autoFocus]);

  /**
   * Handles input value change
   * 
   * @param e - React change event from input element
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
  };

  const submitMessage = () => {
    // Trim whitespace and check if message is not empty
    const trimmedMessage = inputValue.trim();
    if (trimmedMessage && !disabled) {
      // Call onSend callback with the message
      onSend(trimmedMessage);
      // Clear input after sending
      setInputValue('');
    }
  }

  /**
   * Handles form submission (Enter key or Send button click)
   * 
   * @param e - React form event
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    submitMessage();
  };

  /**
   * Handles Enter key press in input field
   * Note: Form submission already handles this, but we can add additional logic here if needed
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Allow Enter key to submit (form handles this)
    if (e.key === 'Enter' && !e.shiftKey) {
      // Prevent default behavior and let form handle submission
	  e.preventDefault()
    submitMessage();
    }
	//shift + enter = new line
  };

  return (
    <form 
      onSubmit={handleSubmit}
      className="flex items-center gap-3 p-4 bg-background border-t border-header"
    >
      {/* Input field */}
      <textarea
        ref={inputRef}
        rows={3}
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        className={`
          flex-1 px-4 py-2 rounded-lg
          bg-header text-text-primary
          placeholder:text-text-muted
          border border-header-light
          focus:outline-none focus:ring-2 focus:ring-user focus:border-transparent
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-all duration-200
        `}
      />

      {/* Send button */}
      <button
        type="submit"
        disabled={disabled || !inputValue.trim()}
        className={`
          flex-shrink-0 w-10 h-10 rounded-full
          bg-user hover:bg-user-dark
          disabled:opacity-50 disabled:cursor-not-allowed
          flex items-center justify-center
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-user focus:ring-offset-2 focus:ring-offset-background
        `}
        aria-label="Send message"
      >
        {/* Upward arrow icon */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="w-5 h-5 text-user-text"
        >
          <line x1="12" y1="19" x2="12" y2="5"></line>
          <polyline points="5 12 12 5 19 12"></polyline>
        </svg>
      </button>
    </form>
  );
}
