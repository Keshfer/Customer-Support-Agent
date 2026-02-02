/**
 * ErrorTrigger Component
 * 
 * Test component that throws an error when a button is clicked.
 * This component is used to test the ErrorBoundary component.
 * 
 * When the button is clicked, the component will throw an error
 * which should be caught by the ErrorBoundary.
 * 
 * WARNING: This component is for testing purposes only.
 * Remove or disable in production.
 */

'use client';

// React hooks for component state
import React, { useState } from 'react';

/**
 * ErrorTrigger component
 * 
 * Component that throws an error when triggered, useful for testing error boundaries.
 */
export default function ErrorTrigger() {
  // State to control whether to throw an error
  // When this is true, the component will throw an error during render
  const [shouldThrowError, setShouldThrowError] = useState(false);

  /**
   * Handle button click to trigger error
   * 
   * Sets state to trigger an error during the next render.
   */
  const handleTriggerError = () => {
    // Set state to true, which will cause the component to throw an error
    setShouldThrowError(true);
  };

  // If shouldThrowError is true, throw an error
  // This error will be caught by the ErrorBoundary
  if (shouldThrowError) {
    throw new Error('Test error triggered by ErrorTrigger component. This is intentional to test the ErrorBoundary.');
  }

  return (
    <button
      onClick={handleTriggerError}
      className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition-colors text-sm"
      title="Click to trigger an error and test the ErrorBoundary"
    >
      🧪 Test Error Boundary
    </button>
  );
}
