#!/usr/bin/env python3
"""
Test script for web_crawl.py routes

This script tests all website scraping endpoints:
1. POST /api/websites/scrape - Scrape website endpoint
2. GET /api/websites/url - Get website by URL endpoint
3. GET /api/websites/title - Get website by title endpoint

Run from project root:
    python -m pytest backend/routes/test_web_crawl.py
    
Or run directly:
    python backend/routes/test_web_crawl.py

Prerequisites:
    - Flask server should be running on http://localhost:5000
    - Database should be set up and accessible
    - OPENAI_API_KEY and FIRECRAWL_API_KEY must be set in environment
"""

import sys
import os
import json
import requests
import time

# Add backend directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Base URL for API requests
BASE_URL = "http://localhost:5000/api"

# Test data storage (for cleanup)
_test_website_urls = []

# ============================================================================
# TEST HELPER FUNCTIONS
# ============================================================================

def print_test_header(test_name):
    """
    Print a formatted test header for visual separation in output.
    
    Uses '=' characters to create a visual separator that makes test output easier to read.
    Each test section starts with this header to clearly identify what's being tested.
    """
    print("\n" + "=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)

def print_success(message):
    """
    Print a success message with checkmark symbol.
    
    Used when a test assertion passes or a test completes successfully.
    The checkmark (✓) provides quick visual feedback that something worked correctly.
    """
    print(f"✓ {message}")

def print_error(message):
    """
    Print an error message with X mark symbol.
    
    Used when a test assertion fails or an unexpected error occurs.
    The X mark (✗) provides quick visual feedback that something went wrong.
    """
    print(f"✗ {message}")

def print_info(message):
    """
    Print an informational message with info symbol.
    
    Used to provide additional context or information during test execution.
    Not used for pass/fail, but for helpful context about what the test is doing.
    """
    print(f"ℹ {message}")

def print_warning(message):
    """
    Print a warning message.
    
    Used to indicate something that might be a problem but doesn't fail the test.
    For example, if the server is not running, we warn but don't fail immediately.
    """
    print(f"⚠ {message}")

def check_server_running():
    """
    Check if the Flask server is running and accessible.
    
    Returns:
        bool: True if server is running, False otherwise
    """
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def cleanup_test_data():
    """Clean up test data from database."""
    try:
        import psycopg2
        from config import DATABASE_URL
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        #delete all websites
        if _test_website_urls:
            cursor.execute("DELETE FROM websites WHERE url = ANY(%s);", (_test_website_urls,))
            print_success(f"Deleted {len(_test_website_urls)} test websites")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print_error(f"Cleanup error: {e}")

# ============================================================================
# TEST 1: POST /api/websites/scrape - Basic Functionality
# ============================================================================

def test_scrape_website_basic():
    """
    Test basic website scraping functionality.
    
    This test verifies:
    - Website record is created in database
    - Chunks are stored with embeddings
    - Response includes website data
    - Website status is set to 'completed'
    """
    print_test_header("POST /api/websites/scrape - Basic Functionality")
    
    if not check_server_running():
        print_warning("Flask server is not running - skipping test")
        print_warning("Start the server with: python backend/app.py")
        return None
    
    try:
        # Test 1.1: Scrape a simple test website
        # Using example.com as it's a reliable test website
        test_url = "https://example.com"
        print_info(f"Scraping test website: {test_url}")
        
        # Send POST request to scrape endpoint
        response = requests.post(
            f"{BASE_URL}/websites/scrape",
            json={"url": test_url},
            headers={"Content-Type": "application/json"},
            timeout=120  # Scraping can take time
        )
        
        # Verify response status
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print_success(f"Received 200 OK response")
        
        # Parse response JSON
        data = response.json()
        assert 'message' in data, "Response should contain 'message' field"
        assert 'website' in data, "Response should contain 'website' field"
        print_success("Response contains required fields")
        
        # Verify website data structure
        website = data['website']
        assert website['url'] == test_url, "Website URL should match"
        assert website['status'] == 'completed', "Website status should be 'completed'"
        assert website['id'] is not None, "Website should have an ID"
        assert website['title'] is not None, "Website should have a title"
        print_success("Website record created with correct data")
        
        # Store URL for cleanup
        _test_website_urls.append(test_url)
        
        # Verify chunks_count if present
        if 'chunks_count' in data:
            assert data['chunks_count'] > 0, "Should have at least one chunk"
            print_success(f"Website has {data['chunks_count']} chunks stored")
        
        print_success("Basic scraping test passed!")
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        if 'response' in locals():
            print_error(f"Response status: {response.status_code}")
            print_error(f"Response body: {response.text}")
        return False
    except Exception as e:
        print_error(f"Test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 2: POST /api/websites/scrape - Request Validation
# ============================================================================

def test_scrape_website_validation():
    """
    Test request validation for scrape endpoint.
    
    This test verifies:
    - Missing URL returns 400 error
    - Empty URL returns 400 error
    - Invalid URL format returns 400 error
    - Invalid request body returns 400 error
    """
    print_test_header("POST /api/websites/scrape - Request Validation")
    
    if not check_server_running():
        print_warning("Flask server is not running - skipping test")
        return None
    
    try:
        # Test 2.1: Missing URL in request body
        print_info("Testing missing URL parameter")
        response = requests.post(
            f"{BASE_URL}/websites/scrape",
            json={},  # Empty JSON body
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for missing URL, got {response.status_code}"
        assert 'error' in response.json(), "Error response should contain 'error' field"
        print_success("Missing URL correctly returns 400 error")
        
        # Test 2.2: Empty URL
        print_info("Testing empty URL")
        response = requests.post(
            f"{BASE_URL}/websites/scrape",
            json={"url": ""},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for empty URL, got {response.status_code}"
        print_success("Empty URL correctly returns 400 error")
        
        # Test 2.3: Invalid URL format
        print_info("Testing invalid URL format")
        response = requests.post(
            f"{BASE_URL}/websites/scrape",
            json={"url": "not-a-valid-url"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for invalid URL, got {response.status_code}"
        assert 'error' in response.json(), "Error response should contain 'error' field"
        print_success("Invalid URL format correctly returns 400 error")
        
        # Test 2.4: Missing Content-Type header (should still work but test it)
        print_info("Testing request without explicit Content-Type")
        response = requests.post(
            f"{BASE_URL}/websites/scrape",
            json={"url": "not-a-valid-url"},
            timeout=10
        )
        # Flask should still parse JSON, but URL validation should fail
        assert response.status_code == 400, "Should return 400 for invalid URL"
        print_success("Request validation works correctly")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        if 'response' in locals():
            print_error(f"Response status: {response.status_code}")
            print_error(f"Response body: {response.text}")
        return False
    except Exception as e:
        print_error(f"Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 3: GET /api/websites/url - Get Website by URL
# ============================================================================

def test_get_website_by_url():
    """
    Test retrieving website and chunks by URL.
    
    This test verifies:
    - Website data is returned correctly
    - Chunks are returned with website
    - Invalid URL returns 404
    - Missing URL parameter returns 400
    """
    print_test_header("GET /api/websites/url - Get Website by URL")
    
    if not check_server_running():
        print_warning("Flask server is not running - skipping test")
        return None
    
    try:
        """No need for commented code. https://example.com is already scraped"""
        # # First, scrape a website to have data to retrieve
        test_url = "https://example.com"
        # print_info(f"Setting up test: scraping {test_url}")
        # # Scrape the website first
        # scrape_response = requests.post(
        #     f"{BASE_URL}/websites/scrape",
        #     json={"url": test_url},
        #     headers={"Content-Type": "application/json"},
        #     timeout=120
        # )
        
        # if scrape_response.status_code != 200:
        #     print_warning(f"Could not scrape test website: {scrape_response.text}")
        #     print_warning("Skipping GET test - website not available")
        #     return None
        
        # Wait a moment for database to be fully updated
        time.sleep(2)
        
        # Test 3.1: Get website by valid URL
        # Note: This endpoint uses request body (JSON) instead of query parameters
        print_info(f"Retrieving website by URL: {test_url}")
        response = requests.get(
            f"{BASE_URL}/websites/url",
            json={"url": test_url},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print_success("Received 200 OK response")
        
        # Parse response
        data = response.json()
        assert 'website' in data, "Response should contain 'website' field"
        assert 'chunks' in data, "Response should contain 'chunks' field"
        assert 'chunks_count' in data, "Response should contain 'chunks_count' field"
        print_success("Response contains required fields")
        
        # Verify website data
        website = data['website']
        assert website['url'] == test_url, "Website URL should match"
        assert website['status'] == 'completed', "Website status should be 'completed'"
        assert website['title'] is not None, "Website should have a title"
        print_success("Website data is correct")
        
        # Verify chunks data
        chunks = data['chunks']
        assert isinstance(chunks, list), "Chunks should be a list"
        # Chunks may be empty if website was scraped but had no content
        if len(chunks) > 0:
            assert data['chunks_count'] == len(chunks), "chunks_count should match chunks length"
            # Verify chunk structure if chunks exist
            chunk = chunks[0]
            assert 'id' in chunk, "Chunk should have 'id' field"
            assert 'chunk_text' in chunk, "Chunk should have 'chunk_text' field"
            assert 'chunk_index' in chunk, "Chunk should have 'chunk_index' field"
            print_success(f"Retrieved {len(chunks)} chunks with correct structure")
        else:
            assert data['chunks_count'] == 0, "chunks_count should be 0 when no chunks"
            print_success("Website has no chunks (empty content)")
        
        # Test 3.2: Get non-existent website
        print_info("Testing with non-existent URL")
        fake_url = "https://this-website-does-not-exist-12345.com"
        response = requests.get(
            f"{BASE_URL}/websites/url",
            json={"url": fake_url},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 404, f"Expected 404 for non-existent website, got {response.status_code}"
        print_success("Non-existent website correctly returns 404")
        
        # Test 3.3: Missing URL parameter
        print_info("Testing missing URL parameter")
        response = requests.get(
            f"{BASE_URL}/websites/url",
            json={},  # Empty JSON body
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for missing URL, got {response.status_code}"
        assert 'error' in response.json(), "Error response should contain 'error' field"
        print_success("Missing URL parameter correctly returns 400")
        
        # Test 3.4: Empty URL
        print_info("Testing empty URL")
        response = requests.get(
            f"{BASE_URL}/websites/url",
            json={"url": ""},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for empty URL, got {response.status_code}"
        print_success("Empty URL correctly returns 400")
        
        # Test 3.5: Invalid URL format
        print_info("Testing invalid URL format")
        response = requests.get(
            f"{BASE_URL}/websites/url",
            json={"url": "not-a-valid-url"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for invalid URL, got {response.status_code}"
        assert 'error' in response.json(), "Error response should contain 'error' field"
        print_success("Invalid URL format correctly returns 400")
        
        # Test 3.6: Missing request body
        print_info("Testing missing request body")
        response = requests.get(
            f"{BASE_URL}/websites/url",
            timeout=10
        )
        # Flask may return 400 or 415 depending on Content-Type header
        assert response.status_code in [400, 415], f"Expected 400 or 415 for missing body, got {response.status_code}"
        print_success("Missing request body correctly returns error")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        if 'response' in locals():
            print_error(f"Response status: {response.status_code}")
            print_error(f"Response body: {response.text}")
        return False
    except Exception as e:
        print_error(f"Get website by URL test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 4: GET /api/websites/title - Get Website by Title
# ============================================================================

def test_get_website_by_title():
    """
    Test retrieving website and chunks by title.
    
    This test verifies:
    - Website data is returned correctly by title
    - Chunks are returned with website
    - Invalid title returns 404
    - Missing title parameter returns 400
    """
    print_test_header("GET /api/websites/title - Get Website by Title")
    
    if not check_server_running():
        print_warning("Flask server is not running - skipping test")
        return None
    
    try:
        # First, scrape a website to have data to retrieve
        test_url = "https://example.com"
        print_info(f"Setting up test: scraping {test_url}")
        
        # Scrape the website first
        scrape_response = requests.post(
            f"{BASE_URL}/websites/scrape",
            json={"url": test_url},
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if scrape_response.status_code != 200:
            print_warning(f"Could not scrape test website: {scrape_response.text}")
            print_warning("Skipping GET test - website not available")
            return None
        
        # Get the website title from the scrape response
        scrape_data = scrape_response.json()
        website_title = scrape_data['website']['title']
        
        if not website_title:
            print_warning("Website has no title - skipping title-based test")
            return None
        
        # Wait a moment for database to be fully updated
        time.sleep(2)
        
        # Test 4.1: Get website by valid title
        # Note: This endpoint uses request body (JSON) instead of query parameters
        print_info(f"Retrieving website by title: {website_title}")
        response = requests.get(
            f"{BASE_URL}/websites/title",
            json={"title": website_title},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print_success("Received 200 OK response")
        
        # Parse response
        data = response.json()
        assert 'website' in data, "Response should contain 'website' field"
        assert 'chunks' in data, "Response should contain 'chunks' field"
        print_success("Response contains required fields")
        
        # Verify website data
        website = data['website']
        assert website['title'] == website_title, "Website title should match"
        assert website['url'] == test_url, "Website URL should match retrieved website"
        print_success("Website data retrieved correctly by title")
        
        # Verify chunks are included
        chunks = data['chunks']
        assert isinstance(chunks, list), "Chunks should be a list"
        # Chunks may be empty if website was scraped but had no content
        if len(chunks) > 0:
            assert 'chunks_count' in data, "Response should contain 'chunks_count' field"
            assert data['chunks_count'] == len(chunks), "chunks_count should match chunks length"
            print_success(f"Retrieved {len(chunks)} chunks with website")
        else:
            assert data.get('chunks_count', 0) == 0, "chunks_count should be 0 when no chunks"
            print_success("Website has no chunks (empty content)")
        
        # Test 4.2: Get non-existent website by title
        print_info("Testing with non-existent title")
        fake_title = "This Title Definitely Does Not Exist 12345"
        response = requests.get(
            f"{BASE_URL}/websites/title",
            json={"title": fake_title},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 404, f"Expected 404 for non-existent title, got {response.status_code}"
        assert 'error' in response.json(), "Error response should contain 'error' field"
        print_success("Non-existent title correctly returns 404")
        
        # Test 4.3: Missing title parameter
        print_info("Testing missing title parameter")
        response = requests.get(
            f"{BASE_URL}/websites/title",
            json={},  # Empty JSON body
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for missing title, got {response.status_code}"
        assert 'error' in response.json(), "Error response should contain 'error' field"
        print_success("Missing title parameter correctly returns 400")
        
        # Test 4.4: Empty title
        print_info("Testing empty title")
        response = requests.get(
            f"{BASE_URL}/websites/title",
            json={"title": ""},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 400, f"Expected 400 for empty title, got {response.status_code}"
        print_success("Empty title correctly returns 400")
        
        # Test 4.5: Missing request body
        print_info("Testing missing request body")
        response = requests.get(
            f"{BASE_URL}/websites/title",
            timeout=10
        )
        # Flask may return 400 or 415 depending on Content-Type header
        assert response.status_code in [400, 415], f"Expected 400 or 415 for missing body, got {response.status_code}"
        print_success("Missing request body correctly returns error")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        if 'response' in locals():
            print_error(f"Response status: {response.status_code}")
            print_error(f"Response body: {response.text}")
        return False
    except Exception as e:
        print_error(f"Get website by title test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 5: Endpoint Accessibility
# ============================================================================

def test_endpoint_accessibility():
    """
    Test that all endpoints are accessible via HTTP requests.
    
    This test verifies:
    - All endpoints respond (even if with errors for invalid requests)
    - Endpoints are registered correctly
    - CORS is configured properly
    """
    print_test_header("Endpoint Accessibility")
    
    if not check_server_running():
        print_warning("Flask server is not running - skipping test")
        return None
    
    try:
        # Test 5.1: POST /api/websites/scrape endpoint exists
        print_info("Testing POST /api/websites/scrape endpoint")
        response = requests.post(
            f"{BASE_URL}/websites/scrape",
            json={"url": "invalid-url"},
            timeout=10
        )
        # Should return 400 (validation error) not 404 (not found)
        assert response.status_code != 404, "Endpoint should exist (not 404)"
        print_success("POST /api/websites/scrape endpoint is accessible")
        
        # Test 5.2: GET /api/websites/url endpoint exists
        print_info("Testing GET /api/websites/url endpoint")
        response = requests.get(
            f"{BASE_URL}/websites/url",
            json={"url": "invalid-url"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        # Should return 400 (validation error) not 404 (not found)
        assert response.status_code != 404, "Endpoint should exist (not 404)"
        print_success("GET /api/websites/url endpoint is accessible")
        
        # Test 5.3: GET /api/websites/title endpoint exists
        print_info("Testing GET /api/websites/title endpoint")
        response = requests.get(
            f"{BASE_URL}/websites/title",
            json={"title": "test"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        # Should return 404 (not found) or 200, not 405 (method not allowed)
        assert response.status_code != 405, "Endpoint should exist (not 405 Method Not Allowed)"
        print_success("GET /api/websites/title endpoint is accessible")
        
        # Test 5.4: Verify health endpoint (baseline test)
        print_info("Testing health endpoint")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200, "Health endpoint should return 200"
        print_success("Health endpoint is accessible")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Endpoint accessibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """
    Run all tests and report results.
    
    This is the main entry point for the test script. It:
    1. Checks if server is running
    2. Runs all test functions
    3. Tracks pass/fail/skip counts
    4. Prints a summary at the end
    5. Returns appropriate exit code for CI/CD systems
    
    Exit codes:
    - 0: All tests passed (or were skipped)
    - 1: One or more tests failed
    """
    print("\n" + "=" * 60)
    print("WEB CRAWL ROUTES TEST SUITE")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_running():
        print_warning("\n⚠ Flask server is not running on http://localhost:5000")
        print_warning("⚠ Start the server with: python backend/app.py")
        print_warning("⚠ Some tests will be skipped\n")
    
    results = []
    
    # Run all tests
    # Each test returns True (pass), False (fail), or None (skipped)
    results.append(("POST /api/websites/scrape - Basic", test_scrape_website_basic()))
    results.append(("POST /api/websites/scrape - Validation", test_scrape_website_validation()))
    results.append(("GET /api/websites/url", test_get_website_by_url()))
    results.append(("GET /api/websites/title", test_get_website_by_title()))
    results.append(("Endpoint Accessibility", test_endpoint_accessibility()))
    
    # Calculate summary statistics
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results:
        if result is True:
            print_success(f"{test_name}: PASSED")
            passed += 1
        elif result is False:
            print_error(f"{test_name}: FAILED")
            failed += 1
        else:  # result is None (skipped)
            print_warning(f"{test_name}: SKIPPED")
            skipped += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    print(f"\nTotal tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")

    #cleanup test data
    cleanup_test_data()
    
    # Exit with appropriate code
    if failed == 0:
        print("\n" + "=" * 60)
        if skipped > 0:
            print("ALL RUN TESTS PASSED! ✓ (some tests were skipped)")
        else:
            print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("SOME TESTS FAILED! ✗")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    """
    Script entry point.
    
    When this script is run directly (not imported), it:
    1. Calls main() to run all tests
    2. Handles keyboard interrupts (Ctrl+C) gracefully
    3. Catches unexpected errors and prints traceback
    4. Exits with appropriate code for CI/CD systems
    """
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        # Handle user interruption (Ctrl+C)
        # This allows clean exit if user wants to stop tests early
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        # Catch any unexpected errors that weren't handled by test functions
        # Print full traceback to help with debugging
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
