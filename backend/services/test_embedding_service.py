#!/usr/bin/env python3
"""
Test script for embedding_service.py

This script tests:
1. generate_embedding() - Single embedding generation with caching
2. generate_embeddings_batch() - Batch embedding generation
3. Caching mechanism - Verify cache works (in-memory and database)
4. Error handling - Invalid inputs, API failures, etc.

Run from project root:
    python backend/services/test_embedding_service.py

Or from backend/services/ directory:
    python test_embedding_service.py

Prerequisites:
    - OPENAI_API_KEY must be set in environment variables
    - OpenAI API must be accessible (requires internet connection)
    - Database should be set up (for database cache testing)
"""

import sys
import os

# Add backend directory to path so we can import modules
# sys.path.insert() adds the specified directory to Python's module search path
# This allows us to import modules from the backend directory structure
# os.path.join() creates a cross-platform path
# os.path.dirname(__file__) gets the directory containing this script
# The '..' goes up one level from services/ to backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the functions we want to test
from services.embedding_service import (
    generate_embedding,
    generate_embeddings_batch,
    _get_embedding_from_db,
    _generate_embedding_from_api,
    openai
)
from config import OPENAI_API_KEY
from services.database_service import create_chunk, create_website, get_db_cursor, close_connection_pool

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

# Test data storage (to clean up after tests)
_test_website_ids = []
_test_chunk_ids = []

def cleanup_test_data():
    """Clean up test data from database."""
    print("\n" + "=" * 60)
    print("CLEANUP: Removing test data")
    print("=" * 60)
    
    try:
        import psycopg2
        from config import DATABASE_URL
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Delete test chunks
        if _test_chunk_ids:
            cursor.execute("DELETE FROM content_chunks WHERE id = ANY(%s);", (_test_chunk_ids,))
            print_success(f"Deleted {len(_test_chunk_ids)} test chunks")
        
        # Delete test websites (cascades to chunks)
        if _test_website_ids:
            cursor.execute("DELETE FROM websites WHERE id = ANY(%s);", (_test_website_ids,))
            print_success(f"Deleted {len(_test_website_ids)} test websites")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Close connection pool
        close_connection_pool()
        print_success("Closed connection pool")
        
    except Exception as e:
        print_error(f"Cleanup error: {e}")

# ============================================================================
# TEST 1: Generate Embedding - Basic Functionality
# ============================================================================

def test_generate_embedding_basic():
    """
    Test basic embedding generation functionality.
    
    This test verifies:
    - Embedding is generated successfully
    - Return value is a list of floats
    - Embedding has correct dimension (1536 for text-embedding-3-small)
    - Function handles valid input correctly
    """
    print_test_header("generate_embedding() - Basic Functionality")
    
    try:
        # Check if API key is available
        if not OPENAI_API_KEY:
            print_warning("OPENAI_API_KEY not set - skipping test")
            return None
        
        if openai is None:
            print_warning("OpenAI client not initialized - skipping test")
            return None
        
        # Test 1.1: Generate embedding for simple text
        # This tests the basic functionality of the embedding service
        test_text = "This is a test sentence for embedding generation."
        print_info(f"Generating embedding for: '{test_text}'")
        
        embedding = generate_embedding(test_text)
        
        # Verify embedding was generated
        assert embedding is not None, "Embedding should not be None"
        print_success("Embedding was generated (not None)")
        
        # Verify embedding is a list
        assert isinstance(embedding, list), "Embedding should be a list"
        print_success("Embedding is a list")
        
        # Verify embedding contains floats
        assert all(isinstance(x, float) for x in embedding), "All elements should be floats"
        print_success("All embedding elements are floats")
        
        # Verify embedding dimension (text-embedding-3-small should be 1536)
        assert len(embedding) == 1536, f"Embedding dimension should be 1536, got {len(embedding)}"
        print_success(f"Embedding has correct dimension: {len(embedding)}")
        
        # Verify embedding values are reasonable (not all zeros, not all same value)
        # Embeddings should have some variation
        unique_values = len(set(embedding))
        assert unique_values > 1, "Embedding should have variation (not all same value)"
        print_success(f"Embedding has variation ({unique_values} unique values)")
        
        # Verify embedding values are in reasonable range (typically -1 to 1, but can vary)
        # Most embedding models produce values in a bounded range
        min_val = min(embedding)
        max_val = max(embedding)
        print_info(f"Embedding value range: [{min_val:.4f}, {max_val:.4f}]")
        
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
# TEST 2: Caching Mechanism - In-Memory Cache
# ============================================================================

def test_caching_mechanism():
    """
    Test that the caching mechanism works correctly.
    
    This test verifies:
    - First call generates embedding (cache miss)
    - Second call with same text uses cache (cache hit)
    - Cache works for identical text
    - Different texts generate different embeddings
    
    Note: This tests @lru_cache functionality which caches function results
    based on function arguments (the text in this case).
    """
    print_test_header("Caching Mechanism - In-Memory Cache")
    
    try:
        # Check if API key is available
        if not OPENAI_API_KEY or openai is None:
            print_warning("OPENAI_API_KEY not set or client not initialized - skipping test")
            return None
        
        # Clear cache by importing and calling cache_clear if available
        # functools.lru_cache provides cache_clear() method on the function
        generate_embedding.cache_clear()
        print_info("Cleared embedding cache")
        
        # Test 2.1: First call (should generate from API)
        test_text = "This is a test for caching mechanism."
        print_info(f"First call with text: '{test_text}'")
        
        import time
        start_time = time.time()
        embedding1 = generate_embedding(test_text)
        first_call_time = time.time() - start_time
        
        assert embedding1 is not None, "First embedding should be generated"
        print_success(f"First embedding generated in {first_call_time:.3f}s")
        
        # Test 2.2: Second call with same text (should use cache)
        # Cache hit should be much faster (near-instant)
        print_info("Second call with same text (should use cache)")
        start_time = time.time()
        embedding2 = generate_embedding(test_text)
        second_call_time = time.time() - start_time
        
        assert embedding2 is not None, "Second embedding should not be None"
        print_success(f"Second embedding retrieved in {second_call_time:.3f}s")
        
        # Verify cache was used (second call should be much faster)
        # Cache hit should be at least 10x faster (usually 100x+ faster)
        if second_call_time < first_call_time / 10:
            if second_call_time == 0:
                print_success(f"Cache hit confirmed (infinitely faster)")
            else:
                print_success(f"Cache hit confirmed ({(first_call_time/second_call_time):.1f}x faster)")
        else:
            if second_call_time == 0:
                print_warning(f"Cache may not be working (both calls took 0 seconds)")
            else:
                print_warning(f"Cache may not be working (only {(first_call_time/second_call_time):.1f}x faster)")
        
        # Verify embeddings are identical (same text = same embedding)
        assert embedding1 == embedding2, "Cached embedding should be identical to original"
        print_success("Cached embedding matches original (identical values)")
        
        # Test 2.3: Different text should generate different embedding
        different_text = "This is a completely different sentence."
        print_info(f"Testing with different text: '{different_text}'")
        embedding3 = generate_embedding(different_text)
        
        assert embedding3 is not None, "Different text should generate embedding"
        assert embedding3 != embedding1, "Different text should produce different embedding"
        print_success("Different text produces different embedding")
        
        # Verify embeddings are actually different (not just different objects)
        # Calculate some difference metric
        differences = sum(abs(a - b) for a, b in zip(embedding1, embedding3))
        assert differences > 0.1, "Embeddings should be significantly different"
        print_success(f"Embeddings are significantly different (total diff: {differences:.4f})")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Caching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 3: Database Caching
# ============================================================================

def test_database_caching():
    """
    Test that database caching works correctly.
    
    This test verifies:
    - Embedding can be retrieved from database
    - Database embedding is used when available
    - Database embedding has correct format and dimension
    
    Note: This requires database setup and creates test data that is cleaned up.
    """
    print_test_header("Database Caching")
    
    global _test_website_ids, _test_chunk_ids
    
    try:
        # Check if API key is available
        if not OPENAI_API_KEY or openai is None:
            print_warning("OPENAI_API_KEY not set or client not initialized - skipping test")
            return None
        
        # Clear in-memory cache to test database cache
        generate_embedding.cache_clear()
        print_info("Cleared in-memory cache")
        
        # Test 3.1: Create test website and chunk with embedding
        # First, generate an embedding for test text
        test_text = "This is test content for database caching."
        print_info(f"Generating embedding for test text: '{test_text}'")
        
        # Generate embedding (this will call API)
        test_embedding = generate_embedding(test_text)
        assert test_embedding is not None, "Should generate embedding for test"
        print_success("Generated test embedding")
        
        # Create test website
        website_id, error = create_website("https://test-cache.example.com", "Test Cache Site", "completed")
        assert error is None, f"Should create website: {error}"
        _test_website_ids.append(website_id)
        print_success(f"Created test website (ID: {website_id})")
        
        # Create chunk with embedding in database
        import json
        chunk_id, error = create_chunk(
            website_id,
            test_text,  # Same text we generated embedding for
            0,  # chunk_index
            test_embedding,  # The embedding we just generated
            json.dumps({"source": "test"})
        )
        assert error is None, f"Should create chunk: {error}"
        _test_chunk_ids.append(chunk_id)
        print_success(f"Created test chunk with embedding (ID: {chunk_id})")
        
        # Test 3.2: Clear cache and retrieve from database
        # Clear in-memory cache so we force database lookup
        generate_embedding.cache_clear()
        print_info("Cleared cache - testing database retrieval")
        
        # Now generate embedding for same text - should come from database
        db_embedding = generate_embedding(test_text)
        
        assert db_embedding is not None, "Should retrieve embedding from database"
        print_success("Retrieved embedding from database")
        
        # Verify embedding matches original
        assert len(db_embedding) == len(test_embedding), "Embedding dimensions should match"
        assert db_embedding == test_embedding, "Database embedding should match original"
        print_success("Database embedding matches original")
        
        # Test 3.3: Verify _get_embedding_from_db function directly
        # Test the internal function that queries database
        direct_db_embedding = _get_embedding_from_db(test_text)
        assert direct_db_embedding is not None, "Direct DB query should return embedding"
        assert direct_db_embedding == test_embedding, "Direct DB query should match"
        print_success("Direct database query works correctly")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Database caching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 4: Batch Embedding Generation
# ============================================================================

def test_generate_embeddings_batch():
    """
    Test batch embedding generation functionality.
    
    This test verifies:
    - Batch function processes multiple texts
    - All embeddings are generated successfully
    - Each embedding has correct dimension
    - Batch processing maintains order
    - Caching works within batch processing
    """
    print_test_header("generate_embeddings_batch() - Batch Processing")
    
    try:
        # Check if API key is available
        if not OPENAI_API_KEY or openai is None:
            print_warning("OPENAI_API_KEY not set or client not initialized - skipping test")
            return None
        
        # Test 4.1: Generate embeddings for multiple texts
        test_texts = [
            "First test sentence for batch processing.",
            "Second test sentence with different content.",
            "Third test sentence to verify batch functionality.",
        ]
        print_info(f"Generating embeddings for {len(test_texts)} texts")
        
        embeddings = generate_embeddings_batch(test_texts)
        
        # Verify results
        assert embeddings is not None, "Batch embeddings should not be None"
        assert isinstance(embeddings, list), "Should return a list"
        assert len(embeddings) == len(test_texts), f"Should return {len(test_texts)} embeddings, got {len(embeddings)}"
        print_success(f"Generated {len(embeddings)} embeddings")
        
        # Verify each embedding
        for i, embedding in enumerate(embeddings):
            assert isinstance(embedding, list), f"Embedding {i} should be a list"
            assert len(embedding) == 1536, f"Embedding {i} should have dimension 1536"
            assert all(isinstance(x, float) for x in embedding), f"Embedding {i} should contain floats"
        print_success("All embeddings have correct format and dimension")
        
        # Test 4.2: Verify embeddings are different (different texts = different embeddings)
        # Check that embeddings are not all identical
        
        #all_same = all(emb == embeddings[0] for emb in embeddings)
        all_different = len(set(tuple(e) for e in embeddings)) == len(embeddings)
        assert all_different, "Different texts should produce different embeddings"
        print_success("Different texts produce different embeddings")
        
        # Test 4.3: Test batch with duplicate texts (should use cache)
        # Clear cache first to see timing difference
        generate_embedding.cache_clear()
        print_info("Testing batch with duplicate texts (cache test)")
        
        duplicate_texts = [
            "Duplicate test sentence.",
            "Duplicate test sentence.",  # Same as first
            "Different test sentence.",
        ]
        
        import time
        start_time = time.time()
        duplicate_embeddings = generate_embeddings_batch(duplicate_texts)
        batch_time = time.time() - start_time
        
        assert duplicate_embeddings is not None, "Should generate embeddings"
        assert len(duplicate_embeddings) == 3, "Should return 3 embeddings"
        
        # First and second should be identical (same text)
        assert duplicate_embeddings[0] == duplicate_embeddings[1], "Duplicate texts should produce identical embeddings"
        print_success("Duplicate texts produce identical embeddings (cache working)")
        
        # Third should be different
        assert duplicate_embeddings[0] != duplicate_embeddings[2], "Different text should produce different embedding"
        print_success(f"Batch processing completed in {batch_time:.3f}s")
        
        # Test 4.4: Test with empty list
        empty_result = generate_embeddings_batch([])
        assert empty_result is None, "Empty list should return None"
        print_success("Empty list handled correctly")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Batch test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 5: Error Handling
# ============================================================================

def test_error_handling():
    """
    Test error handling for various edge cases and invalid inputs.
    
    This test verifies:
    - Empty string handling
    - Whitespace-only string handling
    - None input handling (if applicable)
    - Function returns None on errors (not dict with "error" key)
    """
    print_test_header("Error Handling - Edge Cases")
    
    try:
        # Check if API key is available
        if not OPENAI_API_KEY or openai is None:
            print_warning("OPENAI_API_KEY not set or client not initialized - skipping test")
            return None
        
        # Test 5.1: Empty string
        # Empty strings should return None, not crash
        print_info("Testing with empty string")
        empty_result = generate_embedding("")
        assert empty_result is None, "Empty string should return None"
        print_success("Empty string handled correctly (returns None)")
        
        # Test 5.2: Whitespace-only string
        # Whitespace-only strings should also return None
        print_info("Testing with whitespace-only string")
        whitespace_result = generate_embedding("   \n\t   ")
        assert whitespace_result is None, "Whitespace-only string should return None"
        print_success("Whitespace-only string handled correctly (returns None)")
        
        # Test 5.3: Batch with empty strings
        # Batch should skip empty strings and continue processing
        print_info("Testing batch with mixed valid and empty strings")
        mixed_texts = [
            "Valid text here.",
            "",  # Empty
            "   ",  # Whitespace only
            "Another valid text.",
        ]
        
        mixed_results = generate_embeddings_batch(mixed_texts)
        # Should return embeddings for valid texts only
        assert mixed_results is not None, "Should return results for valid texts"
        assert len(mixed_results) == 2, "Should return embeddings for 2 valid texts only"
        print_success("Batch correctly skips empty/whitespace strings")
        
        # Test 5.4: Verify return type consistency
        # Functions should return None on error, not dict with "error" key
        # (This was a bug in the original code that we fixed)
        error_result = generate_embedding("")
        assert error_result is None or isinstance(error_result, list), \
            "Should return None or list, not dict with 'error' key"
        print_success("Error handling returns correct type (None, not dict)")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# INTEGRATION TEST: Complete Workflow
# ============================================================================

def test_complete_workflow():
    """
    Test the complete embedding workflow from generation to caching.
    
    This test verifies:
    - Generate embedding (API call)
    - Cache in memory (second call uses cache)
    - Store in database
    - Retrieve from database (after cache clear)
    - Batch processing with mixed cached/uncached texts
    """
    print_test_header("Integration Test: Complete Workflow")
    
    global _test_website_ids, _test_chunk_ids
    
    try:
        # Check if API key is available
        if not OPENAI_API_KEY or openai is None:
            print_warning("OPENAI_API_KEY not set or client not initialized - skipping test")
            return None
        
        # Clear all caches
        generate_embedding.cache_clear()
        print_info("Cleared all caches")
        
        # Step 1: Generate embedding (should call API)
        test_text = "Integration test workflow text."
        print_info("Step 1: Generating embedding (API call)")
        
        embedding1 = generate_embedding(test_text)
        assert embedding1 is not None, "Should generate embedding"
        print_success("Step 1: Embedding generated from API")
        
        # Step 2: Second call (should use in-memory cache)
        print_info("Step 2: Second call (should use cache)")
        embedding2 = generate_embedding(test_text)
        assert embedding2 == embedding1, "Should return cached embedding"
        print_success("Step 2: Cache hit confirmed")
        
        # Step 3: Store in database
        print_info("Step 3: Storing embedding in database")
        website_id, _ = create_website("https://workflow-test.example.com", "Workflow Test", "completed")
        _test_website_ids.append(website_id)
        
        import json
        chunk_id, _ = create_chunk(website_id, test_text, 0, embedding1, json.dumps({"source": "test"}))
        _test_chunk_ids.append(chunk_id)
        print_success("Step 3: Embedding stored in database")
        
        # Step 4: Clear cache and retrieve from database
        print_info("Step 4: Clearing cache and retrieving from database")
        generate_embedding.cache_clear()
        
        embedding3 = generate_embedding(test_text)
        assert embedding3 == embedding1, "Should retrieve from database"
        print_success("Step 4: Retrieved from database")
        
        # Step 5: Batch processing with mixed texts
        print_info("Step 5: Batch processing with mixed cached/uncached texts")
        mixed_texts = [
            test_text,  # Should use cache (from step 4)
            "New text for batch processing.",  # Should call API
            test_text,  # Should use cache again
        ]
        
        batch_embeddings = generate_embeddings_batch(mixed_texts)
        assert batch_embeddings is not None, "Should generate batch embeddings"
        assert len(batch_embeddings) == 3, "Should return 3 embeddings"
        assert batch_embeddings[0] == batch_embeddings[2], "Duplicate texts should match"
        print_success("Step 5: Batch processing works with mixed cached/uncached texts")
        
        print_success("Complete workflow test passed!")
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
    print("EMBEDDING SERVICE TEST SUITE")
    print("=" * 60)
    
    # Check prerequisites before running tests
    if not OPENAI_API_KEY:
        print_warning("\n⚠ OPENAI_API_KEY is not set in environment variables")
        print_warning("⚠ Some tests will be skipped")
        print_warning("⚠ Set OPENAI_API_KEY in .env file to run all tests\n")
    
    results = []
    
    # Run all tests
    # Each test returns True (pass), False (fail), or None (skipped)
    results.append(("Generate Embedding - Basic", test_generate_embedding_basic()))
    results.append(("Caching Mechanism", test_caching_mechanism()))
    results.append(("Database Caching", test_database_caching()))
    results.append(("Batch Embedding Generation", test_generate_embeddings_batch()))
    results.append(("Error Handling", test_error_handling()))
    results.append(("Complete Workflow", test_complete_workflow()))
    
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
    
    # Cleanup test data
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
        cleanup_test_data()
        sys.exit(1)
    except Exception as e:
        # Catch any unexpected errors that weren't handled by test functions
        # Print full traceback to help with debugging
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_data()
        sys.exit(1)
