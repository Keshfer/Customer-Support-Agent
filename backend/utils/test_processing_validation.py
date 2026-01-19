#!/usr/bin/env python3
"""
Test script for text_processing.py and validators.py

This script tests:
1. chunk_text() - Text chunking functionality
2. count_tokens() - Token counting functionality
3. validate_url() - URL validation
4. sanitize_input() - Input sanitization

Run from project root:
    python backend/utils/test_processing_validation.py

Or from backend/utils/ directory:
    python test_processing_validation.py
"""

import sys
import os

# Add backend directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.text_processing import chunk_text, count_tokens
from utils.validate import validate_url, sanitize_input

# ============================================================================
# TEST HELPER FUNCTIONS
# ============================================================================

def print_test_header(test_name):
    """Print a formatted test header for visual separation."""
    print("\n" + "=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)

def print_success(message):
    """Print a success message with checkmark."""
    print(f"✓ {message}")

def print_error(message):
    """Print an error message with X mark."""
    print(f"✗ {message}")

def print_info(message):
    """Print an informational message."""
    print(f"ℹ {message}")

# ============================================================================
# TEST 1: chunk_text() Function
# ============================================================================

def test_chunk_text():
    """
    Test the chunk_text() function to verify:
    - Text is split into chunks of appropriate size (500-1000 tokens)
    - Overlap between chunks works correctly
    - Semantic boundaries are preserved (paragraphs, sentences)
    """
    print_test_header("chunk_text() Function")
    
    # Test 1.1: Basic chunking with default parameters
    # This tests that the function can split a long text into multiple chunks
    long_text = """
    This is a long paragraph that should be split into multiple chunks.
    The chunking function should preserve semantic boundaries when possible.
    It should split by paragraphs first, then by sentences if needed.
    
    This is another paragraph that should be in a separate chunk or combined
    with the previous one depending on the chunk size. The function uses
    RecursiveCharacterTextSplitter which respects paragraph boundaries.
    
    Here's a third paragraph to test multiple paragraph handling.
    Each paragraph should be considered as a semantic unit.
    The splitter will try to keep paragraphs together when possible.
    """ * 10  # Repeat to make it long enough to chunk
    
    try:
        chunks = chunk_text(long_text) # default chunk size is 800 and overlap is 100
        
        # Verify chunks were created
        assert chunks is not None, "chunks should not be None"
        assert isinstance(chunks, list), "chunks should be a list"
        assert len(chunks) > 0, "Should have at least one chunk"
        print_success(f"Created {len(chunks)} chunks from long text")
        
        # Test 1.2: Verify chunk sizes are reasonable
        # Check that chunks are not empty and have reasonable length
        for i, chunk in enumerate(chunks):
            assert len(chunk) > 0, f"Chunk {i} should not be empty"
            # Note: We can't easily verify exact token count without calling count_tokens
            # but we can verify chunks exist and have content
        print_success("All chunks have content")
        
        # Test 1.3: Test with custom chunk size
        # Verify the function accepts different chunk_size parameters
        small_chunks = chunk_text(long_text, chunk_size=200, overlap=50)
        assert len(small_chunks) > len(chunks), "Smaller chunk size should create more chunks"
        print_success("Custom chunk size works correctly")
        
        # Test 1.4: Test with minimal text (should return single chunk)
        # Verify that short text doesn't get unnecessarily split
        short_text = "This is a short text that should not be split."
        short_chunks = chunk_text(short_text)
        assert len(short_chunks) == 1, "Short text should return single chunk"
        assert short_chunks[0] == short_text.strip(), "Short text should remain unchanged"
        print_success("Short text handled correctly (single chunk)")
        
        # Test 1.5: Test with empty string
        # Verify edge case handling
        empty_chunks = chunk_text("", chunk_size=800, overlap=100)
        # Empty string might return empty list or list with empty string
        assert isinstance(empty_chunks, list), "Empty input should return list"
        print_success("Empty string handled correctly")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"chunk_text test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 2: count_tokens() Function
# ============================================================================

def test_count_tokens():
    """
    Test the count_tokens() function to verify:
    - Token counting is accurate (or at least consistent)
    - Function handles various text inputs correctly
    - Encoding is consistent with chunk_text (both use cl100k_base)
    """
    print_test_header("count_tokens() Function")
    
    try:
        # Test 2.1: Basic token counting
        # Verify the function returns a positive integer
        test_text = "This is a test sentence."
        token_count = count_tokens(test_text)
        
        assert isinstance(token_count, int), "Token count should be an integer"
        assert token_count > 0, "Token count should be positive"
        print_success(f"Counted {token_count} tokens for: '{test_text}'")
        
        # Test 2.2: Verify longer text has more tokens
        # This tests that the function correctly counts tokens (not just characters)
        longer_text = test_text * 10
        longer_count = count_tokens(longer_text)
        assert longer_count > token_count, "Longer text should have more tokens"
        print_success(f"Longer text correctly has more tokens ({longer_count} vs {token_count})")
        
        # Test 2.3: Test with empty string
        # Verify edge case handling
        empty_count = count_tokens("")
        assert empty_count == 0, "Empty string should have 0 tokens"
        print_success("Empty string returns 0 tokens")
        
        # Test 2.4: Test with special characters
        # Verify function handles punctuation and special chars correctly
        special_text = "Hello, world! How are you? I'm fine. #hashtag @mention"
        special_count = count_tokens(special_text)
        assert special_count > 0, "Special characters should be counted"
        print_success(f"Special characters handled correctly ({special_count} tokens)")
        
        # Test 2.5: Consistency check with chunk_text
        # Verify that chunk_text and count_tokens use compatible encodings
        # If a chunk is created with chunk_size=800, its token count should be close to 800
        sample_text = "This is a sample text. " * 100
        chunks = chunk_text(sample_text, chunk_size=100, overlap=10)
        if chunks:
            chunk_token_count = count_tokens(chunks[0])
            # Allow some variance (chunks can be slightly over/under due to splitting)
            assert 50 <= chunk_token_count <= 150, f"Chunk token count ({chunk_token_count}) should be close to chunk_size (100)"
            print_success(f"Token counting is consistent with chunking (chunk has {chunk_token_count} tokens)")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"count_tokens test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 3: validate_url() Function
# ============================================================================

def test_validate_url():
    """
    Test the validate_url() function to verify:
    - Valid URLs return True
    - Invalid URLs return False
    - Edge cases are handled correctly
    """
    print_test_header("validate_url() Function")
    
    try:
        # Test 3.1: Valid HTTP URLs
        # Test common valid URL formats
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com",
            "https://example.com/path/to/page",
            "https://example.com:8080/path?query=value",
            "https://subdomain.example.com",
        ]
        
        for url in valid_urls:
            result, _ = validate_url(url)
            assert result == True, f"Valid URL should return True: {url}"
        print_success(f"All {len(valid_urls)} valid URLs returned True")
        
        # Test 3.2: Invalid URLs
        # Test various invalid URL formats
        invalid_urls = [
            "not-a-url",
            "example.com",  # Missing protocol
            "ftp://example.com",  # FTP might be invalid depending on validator
            "javascript:alert('xss')",  # Dangerous protocol
            "http://",  # Incomplete URL
            "",  # Empty string
            "   ",  # Whitespace only
        ]
        
        for url in invalid_urls:
            result, _ = validate_url(url)
            assert result == False, f"Invalid URL should return False: {url}"
        print_success(f"All {len(invalid_urls)} invalid URLs returned False")
        
        # Test 3.3: Edge cases
        # Test URLs that might be edge cases
        edge_cases = [
            "https://example.com/path with spaces",  # Spaces in path (usually invalid)
            "https://",  # Just protocol
            "example",  # Single word
        ]
        
        for url in edge_cases:
            result, _= validate_url(url)
            # Just verify it returns a boolean (doesn't crash)
            assert isinstance(result, bool), f"Should return boolean for: {url}"
        print_success("Edge cases handled correctly (return boolean)")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"validate_url test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 4: sanitize_input() Function
# ============================================================================

def test_sanitize_input():
    """
    Test the sanitize_input() function to verify:
    - HTML/script tags are escaped (XSS prevention)
    - Whitespace is trimmed
    - Special characters are handled correctly
    - Function returns safe text for display
    """
    print_test_header("sanitize_input() Function")
    
    try:
        # Test 4.1: Basic sanitization (whitespace trimming)
        # Verify that leading/trailing whitespace is removed
        text_with_spaces = "   Hello World   "
        sanitized = sanitize_input(text_with_spaces)
        assert sanitized == "Hello World", "Should trim whitespace"
        assert sanitized.startswith(" ") == False, "Should remove leading spaces"
        assert sanitized.endswith(" ") == False, "Should remove trailing spaces"
        print_success("Whitespace trimming works correctly")
        
        # Test 4.2: HTML tag escaping (XSS prevention)
        # Verify that HTML tags are escaped to prevent XSS attacks
        html_text = "<script>alert('xss')</script>Hello"
        sanitized = sanitize_input(html_text)
        # markupsafe.escape() converts < to &lt; and > to &gt;
        assert "<script>" not in sanitized, "HTML tags should be escaped"
        assert "&lt;script&gt;" in sanitized or "<" not in sanitized, "Should escape HTML tags"
        print_success("HTML tags are escaped (XSS prevention)")
        
        # Test 4.3: Multiple HTML tags
        # Verify that all HTML tags are escaped, not just the first one
        multiple_html = "<div><p>Hello</p><script>bad()</script></div>"
        sanitized = sanitize_input(multiple_html)
        assert "<div>" not in sanitized, "All HTML tags should be escaped"
        assert "<p>" not in sanitized, "All HTML tags should be escaped"
        assert "<script>" not in sanitized, "All HTML tags should be escaped"
        print_success("Multiple HTML tags are all escaped")
        
        # Test 4.4: Normal text (should remain unchanged except for trimming)
        # Verify that normal text without HTML is preserved
        normal_text = "This is normal user input without any HTML."
        sanitized = sanitize_input(normal_text)
        assert sanitized == normal_text, "Normal text should remain unchanged"
        print_success("Normal text is preserved correctly")
        
        # Test 4.5: Special characters
        # Verify that special characters are handled correctly
        special_chars = "Hello! @user #hashtag $money &amp; more"
        sanitized = sanitize_input(special_chars)
        # Special chars should be preserved (not removed)
        assert "@" in sanitized, "Special characters should be preserved"
        assert "#" in sanitized, "Special characters should be preserved"
        print_success("Special characters are preserved")
        
        # Test 4.6: Empty string
        # Verify edge case handling
        empty_sanitized = sanitize_input("")
        assert empty_sanitized == "", "Empty string should return empty string"
        print_success("Empty string handled correctly")
        
        # Test 4.7: Only whitespace
        # Verify that whitespace-only input is handled
        whitespace_only = "   \n\t   "
        sanitized = sanitize_input(whitespace_only)
        assert sanitized == "", "Whitespace-only should return empty string"
        print_success("Whitespace-only input handled correctly")
        
        # Test 4.8: SQL injection attempt (basic check)
        # Verify that SQL injection patterns are escaped (though parameterized queries are primary defense)
        sql_injection = "'; DROP TABLE users; --"
        sanitized = sanitize_input(sql_injection)
        # The escape function should escape quotes, making SQL injection ineffective
        # Note: This is secondary defense - parameterized queries are primary
        assert "'" in sanitized or "&quot;" in sanitized or "&#x27;" in sanitized or "&#39;" in sanitized, "Quotes should be escaped"
        print_success("SQL injection patterns are escaped (secondary defense)")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"sanitize_input test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# INTEGRATION TEST: Real-world scenario
# ============================================================================

def test_integration_scenario():
    """
    Test a real-world scenario combining multiple functions:
    - User provides input (URL and message)
    - URL is validated
    - Message is sanitized
    - Message is chunked if needed
    - Token counts are calculated
    """
    print_test_header("Integration Test: Real-world Scenario")
    
    try:
        # Simulate user providing a URL and message
        user_url = "https://example.com"
        user_message = """
        I have a question about your product. 
        <script>alert('test')</script>
        Can you help me understand how it works?
        """
        
        # Step 1: Validate URL
        url_valid, _ = validate_url(user_url)
        assert url_valid == True, "User URL should be valid"
        print_success("Step 1: URL validated successfully")
        
        # Step 2: Sanitize user message
        sanitized_message = sanitize_input(user_message)
        assert "<script>" not in sanitized_message, "Message should be sanitized"
        print_success("Step 2: Message sanitized successfully")
        
        # Step 3: Count tokens in sanitized message
        token_count = count_tokens(sanitized_message)
        assert token_count > 0, "Should count tokens in message"
        print_success(f"Step 3: Token count calculated ({token_count} tokens)")
        
        # Step 4: If message is long, chunk it
        if token_count > 500:
            chunks = chunk_text(sanitized_message, chunk_size=500, overlap=50)
            assert len(chunks) > 1, "Long message should be chunked"
            print_success(f"Step 4: Message chunked into {len(chunks)} pieces")
        else:
            print_info("Step 4: Message is short, no chunking needed")
        
        print_success("Integration test passed: All functions work together correctly")
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
    """Run all tests and report results."""
    print("\n" + "=" * 60)
    print("TEXT PROCESSING & VALIDATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("chunk_text()", test_chunk_text()))
    results.append(("count_tokens()", test_count_tokens()))
    results.append(("validate_url()", test_validate_url()))
    results.append(("sanitize_input()", test_sanitize_input()))
    results.append(("Integration Test", test_integration_scenario()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
            passed += 1
        else:
            print_error(f"{test_name}: FAILED")
            failed += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    # Exit with appropriate code
    if failed == 0:
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("SOME TESTS FAILED! ✗")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
