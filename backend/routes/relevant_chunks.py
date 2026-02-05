"""
Relevant Chunks Route

This module provides functions for querying the database to find relevant content chunks
based on user queries. This is used as a function call tool for the LLM.
"""

import logging
from backend.services.embedding_service import generate_embedding
from backend.services.database_service import search_similar_chunks

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def query_database_for_relevant_chunks(user_query: str, limit: int = 5) -> str:
	"""
	Queries the database for relevant content chunks based on a user query.
	
	This function:
	1. Generates an embedding for the user query
	2. Performs vector similarity search to find relevant chunks
	3. Formats the chunks into a readable string format
	
	Args:
		user_query: The user's query/question to search for
		limit: Maximum number of chunks to return (default: 5)
	
	Returns:
		A formatted string containing relevant chunks, or an error message if the search failed.
		The format is:
		Website Title: <title>
		Website URL: <url>
		Chunk Content: <content>
		
		(Repeated for each chunk)
	"""
	try:
		logger.info(f"Querying database for relevant chunks with query: {user_query[:50]}...")
		
		# Step 1: Generate embedding for user query
		# Embeddings are vector representations used for semantic search
		# This allows us to find relevant content chunks based on meaning, not just keywords
		logger.info("Generating embedding for user query")
		query_embedding = generate_embedding(user_query)
		
		if not query_embedding:
			logger.error("Failed to generate embedding for user query")
			return "Error: Failed to generate embedding for the query. Please try again."
		
		# Step 2: Perform vector similarity search to find relevant chunks
		# This searches the content_chunks table for chunks with similar embeddings
		# The search returns the top-k most similar chunks
		logger.info(f"Searching for relevant content chunks using vector similarity (limit: {limit})")
		relevant_chunks, chunks_error = search_similar_chunks(query_embedding, limit=limit)
		
		if chunks_error:
			logger.error(f"Error searching for chunks: {chunks_error}")
			return f"Error: Failed to search database: {chunks_error}"
		
		if not relevant_chunks or len(relevant_chunks) == 0:
			logger.info("No relevant chunks found for the query")
			return "No relevant information found in the database for this query. You may need to scrape a website first using the website_search tool."
		
		logger.info(f"Found {len(relevant_chunks)} relevant chunks")
		
		# Step 3: Format relevant chunks into a readable string
		# Format each chunk with website title, URL, and content
		relevant_chunks_string = ""
		for chunk in relevant_chunks:
			metadata = chunk.get('metadata', {})
			website_title = metadata.get('title', 'Unknown')
			website_url = metadata.get('url', 'Unknown')
			chunk_text = chunk.get('chunk_text', '')
			
			relevant_chunks_string += f"Website Title: {website_title}\n"
			relevant_chunks_string += f"Website URL: {website_url}\n"
			relevant_chunks_string += f"Chunk Content: {chunk_text}\n"
			relevant_chunks_string += "\n\n"  # Double new lines to separate each chunk
		
		return relevant_chunks_string
		
	except Exception as e:
		logger.error(f"Unexpected error querying database: {e}", exc_info=True)
		return f"Error: An unexpected error occurred while querying the database: {str(e)}"
