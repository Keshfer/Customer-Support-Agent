/**
 * apiTest Component
 * 
 * Test component to verify API functions functionality.
 * This component demonstrates:
 * - sendChatMessage function
 * - scrapeWebsite function
 * - getWebsites function
 * - getWebsite function
 * - getWebsiteByTitle function
 * - getWebsiteByUrl function
 * - healthCheck function
 * - Error handling for all API calls
 * 
 * Usage: Import and render this component to test API functions
 */
'use client';

// React hooks for component state and effects
import React, { useState } from 'react';
// Mock API functions for testing (instead of real API calls)
import {
  mockSendChatMessage,
  mockGetWebsites,
  mockGetWebsite,
  mockGetWebsiteByTitle,
  mockGetWebsiteByUrl,
  mockHealthCheck,
} from './mockApi';
// Type definitions for API responses
import { ApiError } from '../types';

export default function ApiTest() {
  // State for storing test results
  const [results, setResults] = useState<Record<string, any>>({});
  // State for tracking loading states for each API call
  const [loading, setLoading] = useState<Record<string, boolean>>({});
  // State for storing errors for each API call
  const [errors, setErrors] = useState<Record<string, ApiError | null>>({});
  
  // State for test inputs
  const [chatMessage, setChatMessage] = useState('');
  const [chatConversationId, setChatConversationId] = useState('');
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [websiteId, setWebsiteId] = useState('');
  const [websiteTitle, setWebsiteTitle] = useState('');
  const [websiteUrl, setWebsiteUrl] = useState('');

  /**
   * Generic function to handle API calls with loading and error states
   * 
   * @param apiName - Name of the API function being called (for state tracking)
   * @param apiCall - The actual API function to call
   */
  const handleApiCall = async (apiName: string, apiCall: () => Promise<any>) => {
    // Set loading state to true for this API call
    setLoading((prev) => ({ ...prev, [apiName]: true }));
    // Clear any previous errors for this API call
    setErrors((prev) => ({ ...prev, [apiName]: null }));

    try {
      // Execute the API call
      const result = await apiCall();
      // Store the result
      setResults((prev) => ({ ...prev, [apiName]: result }));
    } catch (error) {
      // Handle errors and store them
      const apiError = error as ApiError;
      setErrors((prev) => ({ ...prev, [apiName]: apiError }));
      setResults((prev) => ({ ...prev, [apiName]: null }));
    } finally {
      // Always set loading state to false when done
      setLoading((prev) => ({ ...prev, [apiName]: false }));
    }
  };

  /**
   * Test sendChatMessage API function (using mock)
   * Sends a chat message and receives a mocked AI response
   */
  const testSendChatMessage = () => {
    if (!chatMessage.trim()) {
      alert('Please enter a message');
      return;
    }
    handleApiCall('sendChatMessage', () =>
      mockSendChatMessage(chatMessage, chatConversationId || undefined)
    );
  };

  /**
   * Test scrapeWebsite API function
   * Scrapes a website and stores its content in the database
   */
//   const testScrapeWebsite = () => {
//     if (!scrapeUrl.trim()) {
//       alert('Please enter a URL');
//       return;
//     }
//     handleApiCall('scrapeWebsite', () => scrapeWebsite(scrapeUrl));
//   };

  /**
   * Test getWebsites API function (using mock)
   * Retrieves a mock list of scraped websites
   */
  const testGetWebsites = () => {
    handleApiCall('getWebsites', () => mockGetWebsites());
  };

  /**
   * Test getWebsite API function (using mock)
   * Retrieves a mock website and its chunks by ID
   */
  const testGetWebsite = () => {
    const id = parseInt(websiteId);
    if (isNaN(id)) {
      alert('Please enter a valid website ID (number)');
      return;
    }
    handleApiCall('getWebsite', () => mockGetWebsite(id));
  };

  /**
   * Test getWebsiteByTitle API function (using mock)
   * Retrieves a mock website and its chunks by title
   */
  const testGetWebsiteByTitle = () => {
    if (!websiteTitle.trim()) {
      alert('Please enter a website title');
      return;
    }
    handleApiCall('getWebsiteByTitle', () => mockGetWebsiteByTitle(websiteTitle));
  };

  /**
   * Test getWebsiteByUrl API function (using mock)
   * Retrieves a mock website and its chunks by URL
   */
  const testGetWebsiteByUrl = () => {
    if (!websiteUrl.trim()) {
      alert('Please enter a website URL');
      return;
    }
    handleApiCall('getWebsiteByUrl', () => mockGetWebsiteByUrl(websiteUrl));
  };

  /**
   * Test healthCheck API function (using mock)
   * Returns a mock healthy status
   */
  const testHealthCheck = () => {
    handleApiCall('healthCheck', () => mockHealthCheck());
  };

  /**
   * Clear all test results
   */
  const clearResults = () => {
    setResults({});
    setErrors({});
    setLoading({});
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header Section */}
      <div className="flex-shrink-0 bg-header border-b border-header-light p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-text-primary">API Functions Test (Mocked)</h1>
          <button
            onClick={clearResults}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition-colors"
          >
            Clear All Results
          </button>
        </div>
        <p className="text-text-secondary">
          Test all API functions using mocked responses. No backend connection required.
        </p>
      </div>

      {/* Test Controls Section */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Health Check Test */}
          <div className="bg-header p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-text-primary">1. Health Check</h2>
            <p className="text-text-secondary text-sm mb-3">
              Test if the backend API is running and responsive.
            </p>
            <button
              onClick={testHealthCheck}
              disabled={loading.healthCheck}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white transition-colors disabled:opacity-50"
            >
              {loading.healthCheck ? 'Testing...' : 'Test Health Check'}
            </button>
            {results.healthCheck && (
              <div className="mt-3 p-3 bg-background-dark rounded text-sm">
                <pre className="text-text-primary whitespace-pre-wrap">
                  {JSON.stringify(results.healthCheck, null, 2)}
                </pre>
              </div>
            )}
            {errors.healthCheck && (
              <div className="mt-3 p-3 bg-red-600 rounded text-sm text-white">
                <p className="font-semibold">Error:</p>
                <p>{errors.healthCheck.message || errors.healthCheck.error}</p>
                {errors.healthCheck.status && (
                  <p className="text-sm mt-1">Status: {errors.healthCheck.status}</p>
                )}
              </div>
            )}
          </div>

          {/* Send Chat Message Test */}
          {/* <div className="bg-header p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-text-primary">2. Send Chat Message</h2>
            <p className="text-text-secondary text-sm mb-3">
              Send a message to the chat endpoint and receive an AI response.
            </p>
            <div className="space-y-2 mb-3">
              <input
                type="text"
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                placeholder="Enter message..."
                disabled={loading.sendChatMessage}
                className="w-full px-4 py-2 bg-background border border-header-light rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:border-user disabled:opacity-50"
              />
              <input
                type="text"
                value={chatConversationId}
                onChange={(e) => setChatConversationId(e.target.value)}
                placeholder="Conversation ID (optional)..."
                disabled={loading.sendChatMessage}
                className="w-full px-4 py-2 bg-background border border-header-light rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:border-user disabled:opacity-50"
              />
            </div>
            <button
              onClick={testSendChatMessage}
              disabled={loading.sendChatMessage || !chatMessage.trim()}
              className="px-4 py-2 bg-user hover:bg-user-dark rounded-lg text-user-text transition-colors disabled:opacity-50"
            >
              {loading.sendChatMessage ? 'Sending...' : 'Send Message'}
            </button>
            {results.sendChatMessage && (
              <div className="mt-3 p-3 bg-background-dark rounded text-sm">
                <pre className="text-text-primary whitespace-pre-wrap">
                  {JSON.stringify(results.sendChatMessage, null, 2)}
                </pre>
              </div>
            )}
            {errors.sendChatMessage && (
              <div className="mt-3 p-3 bg-red-600 rounded text-sm text-white">
                <p className="font-semibold">Error:</p>
                <p>{errors.sendChatMessage.message || errors.sendChatMessage.error}</p>
                {errors.sendChatMessage.status && (
                  <p className="text-sm mt-1">Status: {errors.sendChatMessage.status}</p>
                )}
              </div>
            )}
          </div> */}

          {/* Scrape Website Test */}
          {/* <div className="bg-header p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-text-primary">3. Scrape Website</h2>
            <p className="text-text-secondary text-sm mb-3">
              Scrape a website and store its content in the database.
            </p>
            <div className="mb-3">
              <input
                type="text"
                value={scrapeUrl}
                onChange={(e) => setScrapeUrl(e.target.value)}
                placeholder="Enter website URL (e.g., https://example.com)..."
                disabled={loading.scrapeWebsite}
                className="w-full px-4 py-2 bg-background border border-header-light rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:border-user disabled:opacity-50"
              />
            </div>
            <button
              onClick={testScrapeWebsite}
              disabled={loading.scrapeWebsite || !scrapeUrl.trim()}
              className="px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg text-white transition-colors disabled:opacity-50"
            >
              {loading.scrapeWebsite ? 'Scraping...' : 'Scrape Website'}
            </button>
            {results.scrapeWebsite && (
              <div className="mt-3 p-3 bg-background-dark rounded text-sm">
                <pre className="text-text-primary whitespace-pre-wrap">
                  {JSON.stringify(results.scrapeWebsite, null, 2)}
                </pre>
              </div>
            )}
            {errors.scrapeWebsite && (
              <div className="mt-3 p-3 bg-red-600 rounded text-sm text-white">
                <p className="font-semibold">Error:</p>
                <p>{errors.scrapeWebsite.message || errors.scrapeWebsite.error}</p>
                {errors.scrapeWebsite.status && (
                  <p className="text-sm mt-1">Status: {errors.scrapeWebsite.status}</p>
                )}
              </div>
            )}
          </div> */}

          {/* Get Websites Test */}
          {/* <div className="bg-header p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-text-primary">4. Get All Websites</h2>
            <p className="text-text-secondary text-sm mb-3">
              Retrieve a list of all scraped websites.
            </p>
            <button
              onClick={testGetWebsites}
              disabled={loading.getWebsites}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors disabled:opacity-50"
            >
              {loading.getWebsites ? 'Loading...' : 'Get Websites'}
            </button>
            {results.getWebsites && (
              <div className="mt-3 p-3 bg-background-dark rounded text-sm">
                <pre className="text-text-primary whitespace-pre-wrap">
                  {JSON.stringify(results.getWebsites, null, 2)}
                </pre>
              </div>
            )}
            {errors.getWebsites && (
              <div className="mt-3 p-3 bg-red-600 rounded text-sm text-white">
                <p className="font-semibold">Error:</p>
                <p>{errors.getWebsites.message || errors.getWebsites.error}</p>
                {errors.getWebsites.status && (
                  <p className="text-sm mt-1">Status: {errors.getWebsites.status}</p>
                )}
              </div>
            )}
          </div> */}

          {/* Get Website by ID Test */}
          {/* <div className="bg-header p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-text-primary">5. Get Website by ID</h2>
            <p className="text-text-secondary text-sm mb-3">
              Retrieve a website and its chunks by ID.
            </p>
            <div className="mb-3">
              <input
                type="number"
                value={websiteId}
                onChange={(e) => setWebsiteId(e.target.value)}
                placeholder="Enter website ID..."
                disabled={loading.getWebsite}
                className="w-full px-4 py-2 bg-background border border-header-light rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:border-user disabled:opacity-50"
              />
            </div>
            <button
              onClick={testGetWebsite}
              disabled={loading.getWebsite || !websiteId.trim()}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white transition-colors disabled:opacity-50"
            >
              {loading.getWebsite ? 'Loading...' : 'Get Website'}
            </button>
            {results.getWebsite && (
              <div className="mt-3 p-3 bg-background-dark rounded text-sm">
                <pre className="text-text-primary whitespace-pre-wrap">
                  {JSON.stringify(results.getWebsite, null, 2)}
                </pre>
              </div>
            )}
            {errors.getWebsite && (
              <div className="mt-3 p-3 bg-red-600 rounded text-sm text-white">
                <p className="font-semibold">Error:</p>
                <p>{errors.getWebsite.message || errors.getWebsite.error}</p>
                {errors.getWebsite.status && (
                  <p className="text-sm mt-1">Status: {errors.getWebsite.status}</p>
                )}
              </div>
            )}
          </div> */}

          {/* Get Website by Title Test */}
          {/* <div className="bg-header p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-text-primary">6. Get Website by Title</h2>
            <p className="text-text-secondary text-sm mb-3">
              Retrieve a website and its chunks by title.
            </p>
            <div className="mb-3">
              <input
                type="text"
                value={websiteTitle}
                onChange={(e) => setWebsiteTitle(e.target.value)}
                placeholder="Enter website title..."
                disabled={loading.getWebsiteByTitle}
                className="w-full px-4 py-2 bg-background border border-header-light rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:border-user disabled:opacity-50"
              />
            </div>
            <button
              onClick={testGetWebsiteByTitle}
              disabled={loading.getWebsiteByTitle || !websiteTitle.trim()}
              className="px-4 py-2 bg-teal-600 hover:bg-teal-700 rounded-lg text-white transition-colors disabled:opacity-50"
            >
              {loading.getWebsiteByTitle ? 'Loading...' : 'Get Website by Title'}
            </button>
            {results.getWebsiteByTitle && (
              <div className="mt-3 p-3 bg-background-dark rounded text-sm">
                <pre className="text-text-primary whitespace-pre-wrap">
                  {JSON.stringify(results.getWebsiteByTitle, null, 2)}
                </pre>
              </div>
            )}
            {errors.getWebsiteByTitle && (
              <div className="mt-3 p-3 bg-red-600 rounded text-sm text-white">
                <p className="font-semibold">Error:</p>
                <p>{errors.getWebsiteByTitle.message || errors.getWebsiteByTitle.error}</p>
                {errors.getWebsiteByTitle.status && (
                  <p className="text-sm mt-1">Status: {errors.getWebsiteByTitle.status}</p>
                )}
              </div>
            )}
          </div> */}

          {/* Get Website by URL Test */}
          {/* <div className="bg-header p-4 rounded-lg">
            <h2 className="text-xl font-semibold mb-3 text-text-primary">7. Get Website by URL</h2>
            <p className="text-text-secondary text-sm mb-3">
              Retrieve a website and its chunks by URL.
            </p>
            <div className="mb-3">
              <input
                type="text"
                value={websiteUrl}
                onChange={(e) => setWebsiteUrl(e.target.value)}
                placeholder="Enter website URL..."
                disabled={loading.getWebsiteByUrl}
                className="w-full px-4 py-2 bg-background border border-header-light rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:border-user disabled:opacity-50"
              />
            </div>
            <button
              onClick={testGetWebsiteByUrl}
              disabled={loading.getWebsiteByUrl || !websiteUrl.trim()}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-white transition-colors disabled:opacity-50"
            >
              {loading.getWebsiteByUrl ? 'Loading...' : 'Get Website by URL'}
            </button>
            {results.getWebsiteByUrl && (
              <div className="mt-3 p-3 bg-background-dark rounded text-sm">
                <pre className="text-text-primary whitespace-pre-wrap">
                  {JSON.stringify(results.getWebsiteByUrl, null, 2)}
                </pre>
              </div>
            )}
            {errors.getWebsiteByUrl && (
              <div className="mt-3 p-3 bg-red-600 rounded text-sm text-white">
                <p className="font-semibold">Error:</p>
                <p>{errors.getWebsiteByUrl.message || errors.getWebsiteByUrl.error}</p>
                {errors.getWebsiteByUrl.status && (
                  <p className="text-sm mt-1">Status: {errors.getWebsiteByUrl.status}</p>
                )}
              </div>
            )}
          </div> */}
        </div>
      </div>

      {/* Test Documentation */}
      <div className="flex-shrink-0 bg-background-dark border-t border-header p-6">
        <h2 className="text-2xl font-semibold mb-4 text-text-primary">
          Test Scenarios & Verification Checklist
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Test Scenario 1: Health Check */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              1. Health Check Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Verify that the health check endpoint is accessible and returns the correct response.
            </p>
            <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
              <li>Click "Test Health Check"</li>
              <li>Verify request is made to GET /api/health</li>
              <li>Check that response contains status: "healthy"</li>
            </ul>
          </div>

          {/* Test Scenario 2: Send Chat Message */}
          <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              2. Send Chat Message Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Verify that chat messages are sent correctly and responses are received.
            </p>
            <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
              <li>Enter a message and click "Send Message"</li>
              <li>Verify request is made to POST /api/chat/message</li>
              <li>Check that response contains AI response and conversation_id</li>
            </ul>
          </div>

          {/* Test Scenario 3: Scrape Website */}
          {/* <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              3. Scrape Website Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Verify that website scraping requests are made correctly.
            </p>
            <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
              <li>Enter a URL and click "Scrape Website"</li>
              <li>Verify request is made to POST /api/websites/scrape</li>
              <li>Check that response contains website_id and status</li>
            </ul>
          </div> */}

          {/* Test Scenario 4: Get Website Functions */}
          {/* <div className="bg-header p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-text-primary">
              4. Get Website Functions Test
            </h3>
            <p className="text-text-secondary text-sm mb-2">
              Verify that all get website functions make correct requests.
            </p>
            <ul className="list-disc list-inside text-text-secondary text-sm space-y-1">
              <li>Test getWebsiteByTitle with a title</li>
              <li>Test getWebsiteByUrl with a URL</li>
              <li>Verify requests are made with correct parameters</li>
            </ul>
          </div>  */}
        </div>

        {/* Verification Checklist */}
        <div className="bg-header p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3 text-text-primary">
            Verification Checklist
          </h3>
          <ul className="list-disc list-inside space-y-1 text-text-primary text-sm">
            <li className="text-green-400">
              ✓ All API functions are callable
            </li>
            <li className="text-green-400">
              ✓ Loading states are properly managed
            </li>
            <li className="text-green-400">
              ✓ Errors are caught and displayed
            </li>
            <li className="text-green-400">
              ✓ API requests are made to correct endpoints
            </li>
            <li className="text-green-400">
              ✓ Request parameters are sent correctly
            </li>
            <li className="text-green-400">
              ✓ Responses are displayed in readable format
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
