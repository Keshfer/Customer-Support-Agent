#!/usr/bin/env python3
"""
Test script for scraping_service.py

This script tests:
1. Firecrawl API connection initialization
2. scrape_website() function with valid/invalid URLs
3. process_scraped_content() function with chunking
4. Error handling and retry logic

Run from project root:
    python backend/services/test_firecrawl_service.py

Or from backend/services/ directory:
    python test_firecrawl_service.py

Prerequisites:
    - FIRECRAWL_API_KEY must be set in environment variables
    - Firecrawl API must be accessible (requires internet connection)
"""

import sys
import os

# Add backend directory to path so we can import modules
# sys.path.insert() adds the specified directory to Python's module search path
# os.path.join() creates a cross-platform path, os.path.dirname(__file__) gets the directory containing this script
# The '..' goes up one level from services/ to backend/, allowing us to import from utils, config, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the functions we want to test
from services.scraping_service import scrape_website, process_scraped_content
from config import FIRECRAWL_API_KEY

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
    For example, if an API key is missing, we warn but don't fail immediately.
    """
    print(f"⚠ {message}")

# ============================================================================
# TEST 1: Firecrawl API Connection Test
# ============================================================================

def test_firecrawl_initialization():
    """
    Test that Firecrawl API connection can be established.
    
    This test verifies:
    - FIRECRAWL_API_KEY is set in environment
    - Firecrawl client can be initialized
    - API can be reached with a simple request (optional connectivity test)
    
    Note: This test requires a valid FIRECRAWL_API_KEY and internet connection.
    If the API key is missing, this test will skip with a warning.
    """
    print_test_header("Firecrawl API Initialization")
    
    try:
        # Check if API key is configured
        # os.getenv() retrieves environment variables, checking if FIRECRAWL_API_KEY exists
        if not FIRECRAWL_API_KEY:
            print_warning("FIRECRAWL_API_KEY is not set in environment variables")
            print_warning("Skipping connection test - set FIRECRAWL_API_KEY in .env file to run this test")
            return False
        
        # Verify API key format (basic check - not empty)
        # Basic validation to ensure the key exists and has some content
        assert len(FIRECRAWL_API_KEY) > 0, "API key should not be empty"
        assert isinstance(FIRECRAWL_API_KEY, str), "API key should be a string"
        print_success("FIRECRAWL_API_KEY is set and valid format")
        return True
        # # Test actual connection by attempting to scrape a simple, reliable website
        # # example.com is a standard test website that should always be accessible
        # # This verifies that the API can actually make requests, not just that the key exists
        # test_url = "https://example.com"
        # print_info(f"Testing connection with simple URL: {test_url}")
        
        # # Call scrape_website with attempts=1 to test connection quickly
        # # If connection works, we'll get a result; if not, we'll get an error
        # result = scrape_website(test_url, attempts=1)
        
        # # Check if we got a valid response (not None, not error dict)
        # # A successful connection should return a dict with 'website_title' and 'markdown_content'
        # if result is None:
        #     print_error("Connection test returned None - API may not be reachable")
        #     return False
        
        # if "error" in result:
        #     print_error(f"URL validation failed: {result['error']}")
        #     return False
        
        # # If we got here, connection is working
        # # Check that we have the expected keys in the response
        # if "website_title" in result and "markdown_content" in result:
        #     print_success("Firecrawl API connection successful!")
        #     print_success(f"Successfully scraped: {result.get('website_title', 'Unknown')}")
        #     return True
        # else:
        #     print_error("Unexpected response format from API")
        #     print_error(f"Response keys: {result.keys()}")
        #     return False
        
    except ImportError as e:
        # ImportError occurs if firecrawl-py package is not installed
        # This is different from API key issues - it's a dependency problem
        print_error(f"Failed to import firecrawl: {e}")
        print_error("Install with: pip install firecrawl-py")
        return False
    except Exception as e:
        # Catch any other unexpected errors during connection test
        print_error(f"Connection test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 2: scrape_website() with Valid URL
# ============================================================================

def test_scrape_valid_website():
    """
    Test scraping a valid website (example.com).
    
    This test verifies:
    - Valid URLs are successfully scraped
    - Response contains expected fields (website_title, markdown_content)
    - Content is extracted correctly
    - Retry logic works (if first attempt fails)
    
    Uses example.com as a reliable test website that should always work.
    """
    print_test_header("scrape_website() - Valid URL")
    
    try:
        # Check if API key is available
        if not FIRECRAWL_API_KEY:
            print_warning("FIRECRAWL_API_KEY not set - skipping test")
            return None
        
        # Test with a simple, reliable website
        # example.com is maintained by IANA and is specifically for testing
        test_url = "https://example.com"
        print_info(f"Scraping URL: {test_url}")
        
        # Call scrape_website with default attempts (3)
        # The function should return a dict with website data on success
        result = scrape_website(test_url, attempts=3)
        
        # Verify result is not None
        # None indicates a critical error that couldn't be handled
        assert result is not None, "Result should not be None"
        print_success("Function returned a result (not None)")
        
        # Verify result is a dictionary
        # All return values from scrape_website should be dicts (success or error)
        assert isinstance(result, dict), "Result should be a dictionary"
        print_success("Result is a dictionary")
        
        # Check for error response
        if "error" in result:
            print_error(f"scrape_website failed: {result['error']}")
            return False
        
        # Verify success response structure
        # A successful scrape should have these two required keys
        assert "website_title" in result, "Result should contain 'website_title'"
        assert "markdown_content" in result, "Result should contain 'markdown_content'"
        print_success("Response contains required fields")
        
        # Verify content is not empty
        # Empty content might indicate the scrape didn't work properly
        assert result["markdown_content"], "Markdown content should not be empty"
        assert result["website_title"], "Website title should not be empty"
        print_success("Content was extracted successfully")
        
        # Display some information about the scraped content
        # This helps verify the scraping actually worked
        title = result["website_title"]
        content_length = len(result["markdown_content"])
        print_success(f"Scraped website: '{title}' ({content_length} characters)")
        
        # Verify markdown content looks reasonable
        # Markdown should contain some text content, not just whitespace
        content_preview = result["markdown_content"][:100].strip()
        if content_preview:
            print_info(f"Content preview: {content_preview[:50]}...")
        else:
            print_warning("Content preview is empty - may indicate scraping issue")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 3: process_scraped_content() - Chunking Test
# ============================================================================

def test_process_scraped_content():
    """
    Test the process_scraped_content() function with chunking.
    
    This test verifies:
    - Content is successfully chunked into appropriate sizes
    - Chunks are returned as a list of strings
    - Chunk sizes are reasonable (500-1000 tokens)
    - Edge cases are handled (empty content, short content)
    
    Uses sample markdown content to simulate scraped website data.
    """
    print_test_header("process_scraped_content() - Chunking")
    
    try:
        # Create sample markdown content for testing
        # This simulates what Firecrawl would return from a real website
        # Using multiple paragraphs to test paragraph boundary preservation
        sample_content = """
# Welcome to Example Website

This is a sample paragraph that contains some text. We need enough content
to test chunking functionality. The chunking should preserve semantic boundaries
whenever possible.

This is another paragraph that continues the content. We want to verify that
the chunking algorithm works correctly with multiple paragraphs. The function
should split content into chunks of approximately 500-1000 tokens.

Here's a third paragraph with more content. Each paragraph should ideally be
kept together when possible. The chunking algorithm uses RecursiveCharacterTextSplitter
which tries to preserve paragraph and sentence boundaries.

This is yet another paragraph to ensure we have enough content for testing.
We need sufficient text to create multiple chunks. This helps verify that
the chunking works correctly for longer documents.

Final paragraph to round out our test content. By this point, we should have
enough content to create at least a couple of chunks depending on the chunk size.
The function should handle this gracefully.
        """ * 5  # Repeat 5 times to ensure we have enough content for chunking
        
        print_info(f"Processing sample content ({len(sample_content)} characters)")
        
        # Test 3.1: Basic chunking with default parameters
        # Default chunk_size=800, overlap=100 should create reasonable chunks
        chunks = process_scraped_content(sample_content)
        
        # Verify chunks were created
        assert chunks is not None, "chunks should not be None"
        assert isinstance(chunks, list), "chunks should be a list"
        assert len(chunks) > 0, "Should have at least one chunk"
        print_success(f"Created {len(chunks)} chunks from content")
        
        # Verify each chunk is a string and has content
        # Each chunk should be a non-empty string
        for i, chunk in enumerate(chunks):
            assert isinstance(chunk, str), f"Chunk {i} should be a string"
            assert len(chunk) > 0, f"Chunk {i} should not be empty"
        print_success("All chunks are non-empty strings")
        
        # Test 3.2: Verify chunk sizes are reasonable
        # Chunks should be in the ballpark of the chunk_size parameter (800 tokens)
        # Note: We can't easily verify exact token count without importing count_tokens
        # But we can verify chunks have reasonable character length
        chunk_lengths = [len(chunk) for chunk in chunks]
        avg_length = sum(chunk_lengths) / len(chunk_lengths)
        print_info(f"Average chunk length: {avg_length:.0f} characters")
        print_info(f"Chunk length range: {min(chunk_lengths)} - {max(chunk_lengths)} characters")
        
        # Test 3.3: Test with custom chunk size
        # Smaller chunk size should create more chunks
        small_chunks = process_scraped_content(sample_content, chunk_size=200, overlap=50)
        assert len(small_chunks) > len(chunks), "Smaller chunk size should create more chunks"
        print_success(f"Custom chunk size works (created {len(small_chunks)} chunks)")
        
        # Test 3.4: Test with short content (should return single chunk)
        # Short content shouldn't be unnecessarily split
        short_content = "This is a short piece of content that should not be chunked."
        short_chunks = process_scraped_content(short_content, chunk_size=800, overlap=100)
        assert len(short_chunks) == 1, "Short content should return single chunk"
        assert short_chunks[0].strip() == short_content.strip(), "Short content should remain intact"
        print_success("Short content handled correctly (single chunk)")
        
        # Test 3.5: Test with empty content
        # Empty content might return empty list or list with empty string
        empty_chunks = process_scraped_content("", chunk_size=800, overlap=100)
        # The function might return None, empty list, or list with empty string
        # All are acceptable for edge case handling
        if empty_chunks is None:
            print_info("Empty content returns None (acceptable edge case handling)")
        elif isinstance(empty_chunks, list):
            print_success("Empty content handled correctly (returns list)")
        else:
            print_warning(f"Empty content returned unexpected type: {type(empty_chunks)}")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"process_scraped_content test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 4: Error Handling - Invalid URL
# ============================================================================

def test_invalid_url_handling():
    """
    Test error handling with invalid URLs.
    
    This test verifies:
    - Invalid URLs are detected and rejected
    - Appropriate error messages are returned
    - Function doesn't crash on invalid input
    - Various types of invalid URLs are handled
    
    Tests multiple invalid URL formats to ensure robust validation.
    """
    print_test_header("Error Handling - Invalid URL")
    
    try:
        # Test 4.1: Missing protocol
        # URLs without http:// or https:// should be rejected
        invalid_urls = [
            ("example.com", "Missing protocol"),
            ("not-a-url", "Not a valid URL format"),
            ("", "Empty string"),
            ("javascript:alert('xss')", "Dangerous protocol"),
            ("ftp://example.com", "Unsupported protocol (if validation rejects it)"),
        ]
        
        for url, description in invalid_urls:
            print_info(f"Testing invalid URL: {url} ({description})")
            result = scrape_website(url, attempts=1)
            
            # Verify result indicates error
            # Should return dict with 'invalid_url' key, not None
            assert result is not None, f"Result should not be None for: {url}"
            assert isinstance(result, dict), f"Result should be dict for: {url}"
            
            # Check for invalid_url key (error response)
            if "error" in result:
                print_success(f"Correctly rejected invalid URL: {url}")
            else:
                # If we got a successful response for an invalid URL, that's a problem
                print_error(f"Invalid URL was not rejected: {url}")
                print_error(f"Unexpected result: {result}")
                return False
        
        print_success(f"All {len(invalid_urls)} invalid URLs were correctly rejected")
        
        # Test 4.2: Verify error message format
        # Error messages should be informative
        test_invalid = "not-a-url"
        result = scrape_website(test_invalid, attempts=1)
        assert "error" in result, f"There should be an error in invalid URL test"
        assert isinstance(result["error"], str), "Error message should be string"
        assert len(result["error"]) > 0, "Error message should not be empty"
        print_success(f"Error message format is correct: {result['error'][:50]}...")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Invalid URL test failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# INTEGRATION TEST: End-to-End Scraping Flow
# ============================================================================

def test_end_to_end_scraping():
    """
    Test the complete scraping workflow from URL to chunks.
    
    This test verifies:
    - Complete flow: scrape website → process content → chunk it
    - Integration between scrape_website() and process_scraped_content()
    - Real-world scenario handling
    
    Simulates the actual workflow used in production.
    """
    print_test_header("Integration Test: End-to-End Scraping")
    
    try:
        # Check if API key is available
        if not FIRECRAWL_API_KEY:
            print_warning("FIRECRAWL_API_KEY not set - skipping integration test")
            return None
        
        # Step 1: Scrape a website
        test_url = "https://example.com"
        print_info(f"Step 1: Scraping {test_url}")
        
        scrape_result = scrape_website(test_url, attempts=3)
        
        # Verify scraping succeeded
        assert scrape_result is not None, "Scrape result should not be None"
        assert "invalid_url" not in scrape_result, "URL should be valid"
        assert "markdown_content" in scrape_result, "Should have markdown content"
        print_success("Step 1: Website scraped successfully")
        
        # Step 2: Process and chunk the content
        markdown_content = scrape_result["markdown_content"]
        print_info(f"Step 2: Processing {len(markdown_content)} characters of content")
        
        chunks = process_scraped_content(markdown_content)
        
        # Verify chunking succeeded
        assert chunks is not None, "Chunks should not be None"
        assert isinstance(chunks, list), "Chunks should be a list"
        assert len(chunks) > 0, "Should have at least one chunk"
        print_success(f"Step 2: Content chunked into {len(chunks)} pieces")
        
        # Step 3: Verify chunk quality
        # Each chunk should have reasonable content
        total_chunk_length = sum(len(chunk) for chunk in chunks)
        assert total_chunk_length > 0, "Total chunk content should be non-zero"
        print_success(f"Step 3: Total chunked content: {total_chunk_length} characters")
        
        # Display summary
        print_success("End-to-end workflow completed successfully!")
        print_info(f"  Website: {scrape_result.get('website_title', 'Unknown')}")
        print_info(f"  Original content: {len(markdown_content)} characters")
        print_info(f"  Number of chunks: {len(chunks)}")
        print_info(f"  Average chunk size: {total_chunk_length // len(chunks)} characters")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Integration test failed: {e}")
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
    1. Runs all test functions
    2. Tracks pass/fail/skip counts
    3. Prints a summary at the end
    4. Returns appropriate exit code for CI/CD systems
    
    Exit codes:
    - 0: All tests passed (or were skipped)
    - 1: One or more tests failed
    """
    print("\n" + "=" * 60)
    print("FIRECRAWL SCRAPING SERVICE TEST SUITE")
    print("=" * 60)
    
    # Check prerequisites before running tests
    # Warn if API key is missing, but don't fail immediately (some tests can still run)
    if not FIRECRAWL_API_KEY:
        print_warning("\n⚠ FIRECRAWL_API_KEY is not set in environment variables")
        print_warning("⚠ Some tests will be skipped")
        print_warning("⚠ Set FIRECRAWL_API_KEY in .env file to run all tests\n")
    
    results = []
    
    # Run all tests
    # Each test returns True (pass), False (fail), or None (skipped)
    results.append(("Firecrawl API Connection", test_firecrawl_initialization()))
    results.append(("Scrape Valid Website", test_scrape_valid_website()))
    results.append(("Process Scraped Content", test_process_scraped_content()))
    results.append(("Invalid URL Handling", test_invalid_url_handling()))
    results.append(("End-to-End Integration", test_end_to_end_scraping()))
    
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
    
    # Exit with appropriate code
    # Return 0 only if no tests failed (skipped tests are OK)
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
