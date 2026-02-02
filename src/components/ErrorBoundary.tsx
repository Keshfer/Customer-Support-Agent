/**
 * ErrorBoundary Component
 * 
 * React Error Boundary component that catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing the entire application.
 * 
 * This component implements the Error Boundary pattern which is a React feature for handling
 * errors in the component tree. It catches errors during rendering, in lifecycle methods,
 * and in constructors of the whole tree below it.
 * 
 * Usage: Wrap components that might throw errors with this ErrorBoundary component.
 * 
 * @example
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 */

'use client';

// React hooks and types for error boundary implementation
import React, { Component, ReactNode } from 'react';

/**
 * Props interface for ErrorBoundary component
 */
interface ErrorBoundaryProps {
  // Child components to wrap with error boundary
  children: ReactNode;
  // Optional fallback component to render when error occurs
  fallback?: ReactNode;
}

/**
 * State interface for ErrorBoundary component
 */
interface ErrorBoundaryState {
  // Boolean indicating if an error has been caught
  hasError: boolean;
  // The error object that was caught (if any)
  error: Error | null;
}

/**
 * ErrorBoundary class component
 * 
 * Catches errors in child components and displays a fallback UI.
 * This is a class component because React Error Boundaries must be class components.
 */
export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  /**
   * Initialize error boundary state
   * 
   * Sets initial state with no error and hasError flag set to false.
   */
  constructor(props: ErrorBoundaryProps) {
    super(props);
    // Initialize state: no error has occurred yet
    this.state = {
      hasError: false,
      error: null,
    };
  }

  /**
   * Static method to update state when an error is caught
   * 
   * This method is called during the "render" phase, so side-effects are not permitted.
   * It should return an object to update state, or null to update nothing.
   * 
   * @param error - The error that was thrown
   * @returns State update object with hasError set to true and the error
   */
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  /**
   * Lifecycle method called after an error has been thrown by a descendant component
   * 
   * This method is called during the "commit" phase, so side-effects are permitted.
   * Use it for logging errors, sending error reports to error reporting services, etc.
   * 
   * @param error - The error that was thrown
   * @param errorInfo - Additional error information (component stack)
   */
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to console for debugging
    // In production, you might want to send this to an error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  /**
   * Handle resetting the error boundary
   * 
   * Clears the error state, allowing the component tree to re-render.
   * This can be called after fixing the issue that caused the error.
   */
  handleReset = () => {
    // Reset error state to allow re-rendering of child components
    this.setState({
      hasError: false,
      error: null,
    });
  };

  /**
   * Render method
   * 
   * If an error has been caught, render the fallback UI.
   * Otherwise, render the children normally.
   */
  render() {
    // If an error has been caught, render fallback UI
    if (this.state.hasError) {
      // Use custom fallback if provided, otherwise use default
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-header p-6 rounded-lg border border-header-light">
            <h2 className="text-2xl font-bold text-text-primary mb-4">
              Something went wrong
            </h2>
            <p className="text-text-secondary mb-4">
              An unexpected error occurred. Please try refreshing the page or contact support if the problem persists.
            </p>
            {/* {this.state.error && (
              <details className="mb-4">
                <summary className="text-text-secondary cursor-pointer mb-2">
                  Error Details
                </summary>
                <pre className="text-xs text-text-secondary bg-background-dark p-3 rounded overflow-auto">
                  {this.state.error.toString()}
                  {this.state.error.stack && (
                    <>
                      {'\n\n'}
                      {this.state.error.stack}
                    </>
                  )}
                </pre>
              </details>
            )} */}
            <div className="flex gap-3">
              <button
                onClick={this.handleReset}
                className="px-4 py-2 bg-user hover:bg-user-dark rounded-lg text-user-text transition-colors"
              >
                Try Again
              </button>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-header-light hover:bg-header rounded-lg text-text-primary transition-colors"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    // No error: render children normally
    return this.props.children;
  }
}
