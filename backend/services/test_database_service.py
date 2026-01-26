#!/usr/bin/env python3
"""
Test script for database_service.py

This script tests all database service functions:
1. Database connection
2. Website CRUD operations
3. Content chunk CRUD operations
4. Vector similarity search
5. Message/conversation storage

Run from project root:
    python backend/services/test_database_service.py

Or from backend/services/ directory:
    python test_database_service.py
"""

import sys
import os
import json

# Add backend directory to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


from services.database_service import (
    get_connection_pool,
    get_db_connection,
    create_website,
    get_website_by_url,
    get_website_by_title,
    get_all_websites,
    update_website_status_by_url,
    update_website_title_by_url,
    create_chunk_by_url,
    get_chunks_by_website_url,
    get_chunk_by_url_and_index,
    search_similar_chunks,
    save_message,
    get_conversation_history,
    close_connection_pool
)

# Test data storage (to clean up after tests)
_test_website_urls = []  # Track URLs instead of IDs
_test_chunk_ids = []
_test_conversation_id = "test_conv_12345"

def print_test_header(test_name):
    """Print a formatted test header."""
    print("\n" + "=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)

def print_success(message):
    """Print a success message."""
    print(f"✓ {message}")

def print_error(message):
    """Print an error message."""
    print(f"✗ {message}")

def cleanup_test_data():
    """Clean up test data from database."""
    print("\n" + "=" * 60)
    print("CLEANUP: Removing test data")
    print("=" * 60)
    
    import psycopg2
    from config import DATABASE_URL
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Delete test chunks
        if _test_chunk_ids:
            cursor.execute("DELETE FROM content_chunks WHERE id = ANY(%s);", (_test_chunk_ids,))
            print_success(f"Deleted {len(_test_chunk_ids)} test chunks")
        
        # Delete test websites (cascades to chunks)
        if _test_website_urls:
            cursor.execute("DELETE FROM websites WHERE url = ANY(%s);", (_test_website_urls,))
            print_success(f"Deleted {len(_test_website_urls)} test websites")
        
        # Delete test messages
        cursor.execute("DELETE FROM messages WHERE conversation_id = %s;", (_test_conversation_id,))
        print_success("Deleted test messages")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Close connection pool
        close_connection_pool()
        print_success("Closed connection pool")
        
    except Exception as e:
        print_error(f"Cleanup error: {e}")

# ============================================================================
# TEST 1: Database Connection
# ============================================================================

def test_database_connection():
    """
    Test that we can successfully connect to the database.
    
    Uses get_connection_pool() to create/retrieve a connection pool,
    then get_db_connection() context manager to get a connection.
    The 'with' statement automatically handles connection cleanup.
    """
    print_test_header("Database Connection")
    
    try:
        # Test connection pool creation
        pool = get_connection_pool()
        assert pool is not None, "Connection pool should not be None"
        print_success("Connection pool created/retrieved")
        
        # Test getting a connection from the pool
        # 'with' statement ensures connection is returned to pool even if error occurs
        with get_db_connection() as conn:
            assert conn is not None, "Connection should not be None"
            print_success("Successfully obtained connection from pool")
            
            # Test that connection is active
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            assert result[0] == 1, "Should return 1 from test query"
            cursor.close()
            print_success("Connection is active and can execute queries")
        
        print_success("Connection successfully returned to pool")
        return True
        
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False

# ============================================================================
# TEST 2: Website CRUD Operations
# ============================================================================

def test_website_operations():
    """
    Test creating a website, retrieving it, and verifying the data.
    
    Tests:
    - create_website(): Creates a new website record, returns (id, None) on success
    - get_website_by_url(): Retrieves website by URL, returns (dict, None) on success
    - get_website_by_title(): Retrieves website by title, returns (dict, None) on success
    - get_all_websites(): Gets all websites, returns (list, None) on success
    - update_website_status_by_url(): Updates website status by URL, returns (True, None) on success
    - update_website_title_by_url(): Updates website title by URL, returns (True, None) on success
    """
    print_test_header("Website CRUD Operations")
    
    global _test_website_urls
    
    try:
        # Test 2.1: Create website
        test_url = "https://test-example.com"
        test_title = "Test Website"
        test_status = "pending"
        
        website_id, error = create_website(test_url, test_title, test_status)
        assert error is None, f"Should not have error: {error}"
        assert website_id is not None, "Website ID should not be None"
        assert isinstance(website_id, int), "Website ID should be an integer"
        _test_website_urls.append(test_url)
        print_success(f"Created website with URL: {test_url}")
        
        # Test 2.2: Retrieve website by URL
        website_data, error = get_website_by_url(test_url)
        assert error is None, f"Should not have error: {error}"
        assert website_data is not None, "Website data should not be None"
        assert website_data['id'] == website_id, "Website ID should match"
        assert website_data['url'] == test_url, "URL should match"
        assert website_data['title'] == test_title, "Title should match"
        assert website_data['status'] == test_status, "Status should match"
        print(f"Scraped at {website_data['scraped_at']}")
        print_success("Retrieved website by URL and verified all fields")
        
        # Test 2.2b: Retrieve website by title
        website_data_by_title, error = get_website_by_title(test_title)
        assert error is None, f"Should not have error: {error}"
        assert website_data_by_title is not None, "Website data should not be None"
        assert website_data_by_title['url'] == test_url, "URL should match when retrieved by title"
        print_success("Retrieved website by title and verified URL matches")
        
        # Test 2.3: Get all websites
        all_websites, error = get_all_websites()
        assert error is None, f"Should not have error: {error}"
        assert all_websites is not None, "Website list should not be None"
        assert isinstance(all_websites, list), "Should return a list"
        assert len(all_websites) > 0, "Should have at least one website"
        
        # Verify our test website is in the list
        found = False
        for w in all_websites:
            if w['url'] == test_url:
                found = True
                assert w['title'] == test_title, "Title should match in list"
                break
        assert found, "Test website should be in the list"
        print_success(f"Retrieved all websites ({len(all_websites)} total)")
        
        # Test 2.4: Update website status by URL
        new_status = "completed"
        success, error = update_website_status_by_url(test_url, new_status)
        assert error is None, f"Should not have error: {error}"
        assert success is True, "Update should return True"
        
        # Verify status was updated
        updated_website, error = get_website_by_url(test_url)
        assert updated_website['status'] == new_status, "Status should be updated to completed"
        print_success(f"Updated website status to: {new_status}")
        
        # Test 2.5: Update website title by URL
        new_title = "Updated Test Website"
        success, error = update_website_title_by_url(test_url, new_title)
        assert error is None, f"Should not have error: {error}"
        assert success is True, "Title update should return True"
        
        # Verify title was updated
        updated_website, error = get_website_by_url(test_url)
        assert updated_website['title'] == new_title, "Title should be updated"
        print_success(f"Updated website title to: {new_title}")
        
        # Test 2.6: Test error handling - get non-existent website
        fake_url = "https://fake-nonexistent-website-12345.com"
        website_data, error = get_website_by_url(fake_url)
        assert website_data is None, "Should return None for non-existent website"
        assert error is not None, "Should return error message"
        assert "not found" in error.lower(), "Error should mention not found"
        print_success("Error handling works for non-existent website")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Website operations test failed: {e}")
        return False

# ============================================================================
# TEST 3: Content Chunk Operations
# ============================================================================

def test_chunk_operations():
    """
    Test creating chunks and retrieving them by website URL.
    
    Tests:
    - create_chunk_by_url(): Creates a content chunk with embedding by URL, returns (id, None)
    - get_chunks_by_website_url(): Gets all chunks for a website by URL, returns (list, None)
    - get_chunk_by_url_and_index(): Gets a single chunk by URL and index, returns (dict, None)
    """
    print_test_header("Content Chunk Operations")
    
    global _test_chunk_ids, _test_website_urls
    
    try:
        # First, create a test website
        test_url = "https://chunk-test.com"
        website_id, _ = create_website(test_url, "Chunk Test Site", "completed")
        _test_website_urls.append(test_url)
        
        # Test 3.1: Create chunk with embedding
        # Create a sample embedding vector (1536 dimensions for OpenAI ada-002)
        # Using small values for testing
        test_embedding = [0.1] * 1536  # List of 1536 float values
        
        test_chunk_text = "This is a test chunk of content for testing purposes."
        test_chunk_index = 0
        test_metadata = json.dumps({"source": "test", "type": "paragraph"})
        
        chunk_id, error = create_chunk_by_url(
            test_url, 
            test_chunk_text, 
            test_chunk_index, 
            test_embedding, 
            test_metadata
        )
        assert error is None, f"Should not have error: {error}"
        assert chunk_id is not None, "Chunk ID should not be None"
        assert isinstance(chunk_id, int), "Chunk ID should be an integer"
        _test_chunk_ids.append(chunk_id)
        print_success(f"Created chunk with ID: {chunk_id}")
        
        # Test 3.2: Create another chunk for the same website
        test_chunk_text2 = "This is another test chunk for the same website."
        chunk_id2, error = create_chunk_by_url(
            test_url,
            test_chunk_text2,
            1,  # chunk_index
            [0.2] * 1536,  # Different embedding
            json.dumps({"source": "test", "type": "paragraph"})
        )
        assert error is None, "Should not have error"
        _test_chunk_ids.append(chunk_id2)
        print_success(f"Created second chunk with ID: {chunk_id2}")
        
        # Test 3.3: Get chunks by website URL
        chunks, error = get_chunks_by_website_url(test_url)
        assert error is None, f"Should not have error: {error}"
        assert chunks is not None, "Chunks list should not be None"
        assert isinstance(chunks, list), "Should return a list"
        assert len(chunks) >= 2, "Should have at least 2 chunks"
        
        # Verify chunk data
        found_chunk1 = False
        found_chunk2 = False
        for chunk in chunks:
            assert 'id' in chunk, "Chunk should have 'id' field"
            assert 'website_id' in chunk, "Chunk should have 'website_id' field"
            assert 'chunk_text' in chunk, "Chunk should have 'chunk_text' field"
            assert chunk['website_id'] == website_id, "All chunks should belong to test website"
            
            if chunk['id'] == chunk_id:
                found_chunk1 = True
                assert chunk['chunk_text'] == test_chunk_text, "Chunk text should match"
                assert chunk['chunk_index'] == test_chunk_index, "Chunk index should match"
            elif chunk['id'] == chunk_id2:
                found_chunk2 = True
                assert chunk['chunk_text'] == test_chunk_text2, "Second chunk text should match"
        
        assert found_chunk1, "First chunk should be in the list"
        assert found_chunk2, "Second chunk should be in the list"
        print_success(f"Retrieved {len(chunks)} chunks for website")
        
        # Test 3.4: Get single chunk by URL and index
        chunk_data, error = get_chunk_by_url_and_index(test_url, test_chunk_index)
        assert error is None, f"Should not have error: {error}"
        assert chunk_data is not None, "Chunk data should not be None"
        assert chunk_data['chunk_index'] == test_chunk_index, "Chunk index should match"
        assert chunk_data['chunk_text'] == test_chunk_text, "Chunk text should match"
        print_success("Retrieved single chunk by URL and index and verified data")
        
        # Test 3.5: Test error handling - get chunks for non-existent website
        fake_url = "https://fake-nonexistent-website-99999.com"
        chunks, error = get_chunks_by_website_url(fake_url)
        assert chunks is None or len(chunks) == 0 or error is not None, "Should handle non-existent website"
        print_success("Error handling works for non-existent website")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Chunk operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 4: Vector Similarity Search
# ============================================================================

def test_vector_similarity_search():
    """
    Test vector similarity search with sample embeddings.
    
    Tests search_similar_chunks() which uses PostgreSQL's <=> operator
    (cosine distance) to find similar chunks based on embedding vectors.
    Returns chunks ordered by similarity (lowest distance = most similar).
    """
    print_test_header("Vector Similarity Search")
    
    global _test_chunk_ids, _test_website_urls
    
    try:
        # Create a test website
        test_url = "https://vector-test.com"
        website_id, _ = create_website(test_url, "Vector Test", "completed")
        _test_website_urls.append(test_url)
        
        # Create multiple chunks with different embeddings
        # Embedding 1: All 0.1s (will be our query target)
        target_embedding = [0.1] * 1536
        chunk1_id, _ = create_chunk_by_url(
            test_url,
            "This chunk has embedding with all 0.1 values",
            0,
            target_embedding,
            json.dumps({"type": "target"})
        )
        _test_chunk_ids.append(chunk1_id)
        
        # Embedding 2: All 0.2s (less similar)
        chunk2_id, _ = create_chunk_by_url(
            test_url,
            "This chunk has embedding with all 0.2 values",
            1,
            [0.2] * 1536,
            json.dumps({"type": "different"})
        )
        _test_chunk_ids.append(chunk2_id)
        
        # Embedding 3: All 0.9s (very different)
        chunk3_id, _ = create_chunk_by_url(
            test_url,
            "This chunk has embedding with all 0.9 values",
            2,
            [0.9] * 1536,
            json.dumps({"type": "very_different"})
        )
        _test_chunk_ids.append(chunk3_id)
        
        print_success("Created 3 test chunks with different embeddings")
        
        # Test 4.1: Search for similar chunks using target embedding
        # search_similar_chunks() takes a list of floats (embedding vector) and limit
        # Returns (list of dicts, None) where each dict has chunk data + 'distance' field
        similar_chunks, error = search_similar_chunks(target_embedding, limit=5)
        assert error is None, f"Should not have error: {error}"
        assert similar_chunks is not None, "Similar chunks should not be None"
        assert isinstance(similar_chunks, list), "Should return a list"
        assert len(similar_chunks) >= 3, "Should find at least 3 chunks"
        
        print_success(f"Found {len(similar_chunks)} similar chunks")
        
        # Test 4.2: Verify results are ordered by similarity (distance ascending)
        # Distance of 0.0 means identical, higher values mean less similar
        distances = [chunk['distance'] for chunk in similar_chunks]
        assert distances == sorted(distances), "Chunks should be ordered by distance (ascending)"
        print_success("Chunks are correctly ordered by similarity")
        
        # Test 4.3: Verify the most similar chunk is our target
        # Find the chunk with chunk_index 0 (our target chunk)
        most_similar = None
        for chunk in similar_chunks:
            if chunk.get('chunk_index') == 0 and "0.1 values" in chunk.get('chunk_text', ''):
                most_similar = chunk
                break
        
        # If not found by index, check the first few results
        if not most_similar and len(similar_chunks) > 0:
            most_similar = similar_chunks[0]
        
        assert most_similar is not None, "Should find the target chunk"
        assert "0.1 values" in most_similar.get('chunk_text', ''), "Most similar should be chunk with target embedding"
        assert most_similar['distance'] < 0.1, "Distance to identical embedding should be very small"
        print_success("Most similar chunk is correctly identified")
        
        # Test 4.4: Verify distance values are floats
        for chunk in similar_chunks:
            assert 'distance' in chunk, "Each chunk should have 'distance' field"
            assert isinstance(chunk['distance'], float), "Distance should be a float"
            assert chunk['distance'] >= 0, "Distance should be non-negative"
        print_success("All distance values are valid floats")
        
        # Test 4.5: Test with limit parameter
        limited_chunks, error = search_similar_chunks(target_embedding, limit=2)
        assert len(limited_chunks) <= 2, "Should respect limit parameter"
        print_success("Limit parameter works correctly")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Vector similarity search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 5: Message/Conversation Storage
# ============================================================================

def test_message_operations():
    """
    Test saving messages and retrieving conversation history.
    
    Tests:
    - save_message(): Saves a message to database, returns (message_id, None)
    - get_conversation_history(): Gets all messages for a conversation,
      returns (list of dicts, None) ordered by timestamp
    """
    print_test_header("Message/Conversation Storage")
    
    try:
        # Test 5.1: Save user message
        user_message = "Hello, I need help with my account"
        message_id1, error = save_message(_test_conversation_id, user_message, "user")
        assert error is None, f"Should not have error: {error}"
        assert message_id1 is not None, "Message ID should not be None"
        assert isinstance(message_id1, int), "Message ID should be an integer"
        print_success(f"Saved user message with ID: {message_id1}")
        
        # Test 5.2: Save agent message
        agent_message = "I'd be happy to help you with your account. What do you need?"
        message_id2, error = save_message(_test_conversation_id, agent_message, "agent")
        assert error is None, "Should not have error"
        assert message_id2 is not None, "Message ID should not be None"
        print_success(f"Saved agent message with ID: {message_id2}")
        
        # Test 5.3: Save another user message
        user_message2 = "I want to upgrade my plan"
        message_id3, error = save_message(_test_conversation_id, user_message2, "user")
        assert error is None, "Should not have error"
        print_success(f"Saved second user message with ID: {message_id3}")
        
        # Test 5.4: Get conversation history
        # get_conversation_history() returns (list of message dicts, None)
        # Each dict has: id, conversation_id, message, sender, timestamp
        messages, error = get_conversation_history(_test_conversation_id)
        assert error is None, f"Should not have error: {error}"
        assert messages is not None, "Messages list should not be None"
        assert isinstance(messages, list), "Should return a list"
        assert len(messages) == 3, "Should have 3 messages"
        print_success(f"Retrieved conversation history with {len(messages)} messages")
        
        # Test 5.5: Verify messages are ordered by timestamp (ascending)
        timestamps = [msg['timestamp'] for msg in messages]
        assert timestamps == sorted(timestamps), "Messages should be ordered by timestamp (ascending)"
        print_success("Messages are correctly ordered by timestamp")
        
        # Test 5.6: Verify message data
        assert messages[0]['message'] == user_message, "First message should match"
        assert messages[0]['sender'] == "user", "First message sender should be 'user'"
        assert messages[0]['conversation_id'] == _test_conversation_id, "Conversation ID should match"
        
        assert messages[1]['message'] == agent_message, "Second message should match"
        assert messages[1]['sender'] == "agent", "Second message sender should be 'agent'"
        
        assert messages[2]['message'] == user_message2, "Third message should match"
        assert messages[2]['sender'] == "user", "Third message sender should be 'user'"
        
        # Verify all messages have required fields
        for msg in messages:
            assert 'id' in msg, "Message should have 'id' field"
            assert 'conversation_id' in msg, "Message should have 'conversation_id' field"
            assert 'message' in msg, "Message should have 'message' field"
            assert 'sender' in msg, "Message should have 'sender' field"
            assert 'timestamp' in msg, "Message should have 'timestamp' field"
            assert msg['sender'] in ['user', 'agent'], "Sender should be 'user' or 'agent'"
        
        print_success("All message data is correct and complete")
        
        # Test 5.7: Test error handling - get non-existent conversation
        fake_conv_id = "fake_conversation_999"
        messages, error = get_conversation_history(fake_conv_id)
        assert messages is None or len(messages) == 0 or error is not None, "Should handle non-existent conversation"
        print_success("Error handling works for non-existent conversation")
        
        return True
        
    except AssertionError as e:
        print_error(f"Assertion failed: {e}")
        return False
    except Exception as e:
        print_error(f"Message operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run all tests and report results."""
    print("\n" + "=" * 60)
    print("DATABASE SERVICE TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Website Operations", test_website_operations()))
    results.append(("Chunk Operations", test_chunk_operations()))
    results.append(("Vector Similarity Search", test_vector_similarity_search()))
    results.append(("Message Operations", test_message_operations()))
    
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
    
    # Cleanup
    cleanup_test_data()
    
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
        cleanup_test_data()
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_test_data()
        sys.exit(1)
