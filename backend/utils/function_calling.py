"""
Function calling utility for handling LLM function/tool calls.

This module provides a call_function() function that routes LLM function calls
to their corresponding handler functions. Currently supports:
- website_search: Scrapes a website and stores its content
- query_database: Searches the database for relevant content chunks
"""

import logging
from backend.routes.web_crawl import scrape_and_store_website
from backend.routes.relevant_chunks import query_database_for_relevant_chunks

# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def call_function(name: str, args: dict) -> str:
	"""
	Handles function calls from the LLM by routing to appropriate handler functions.
	
	This function acts as a dispatcher that routes function calls based on the function name.
	Each function call is handled by its corresponding implementation.
	
	Args:
		name: The name of the function to call (e.g., "website_search")
		args: Dictionary of arguments for the function call
	
	Returns:
		A string representation of the function call result. This can be:
		- Success message with details
		- Error message if the function call failed
		- JSON string for complex results
	
	Example:
		>>> result = call_function("website_search", {"website_url": "https://example.com"})
		>>> print(result)
		"Website scraped successfully. Title: Example Website, Chunks: 5"
	"""
	if name == "website_search":
		# Extract website_url from arguments
		website_url = args.get('website_url', '')
		
		if not website_url:
			logger.error("website_search called without website_url argument")
			return "Error: website_url is required for website_search function"
		
		logger.info(f"Handling website_search function call for URL: {website_url}")
		
		# Call the scraping helper function
		result = scrape_and_store_website(website_url)
		
		# Format result as a string for the LLM
		if result.get('success', False):
			website = result.get('website', {})
			website_title = website.get('title', 'Unknown')
			chunks_count = result.get('chunks_count', 0)
			
			# Build success message
			message = f"Website scraped successfully. "
			message += f"Title: {website_title}, "
			message += f"Chunks stored: {chunks_count}"
			
			if 'message' in result:
				message = result['message'] + f" Title: {website_title}, Chunks: {chunks_count}"
			
			logger.info(f"Website search completed successfully: {website_title}")
			return message
		else:
			# Build error message
			error_msg = result.get('error', 'Unknown error occurred')
			logger.error(f"Website search failed: {error_msg}")
			return f"Error scraping website: {error_msg}"
	elif name == "query_database":
		# Extract user_query from arguments
		user_query = args.get('user_query', '')
		
		if not user_query:
			logger.error("query_database called without user_query argument")
			return "Error: user_query is required for query_database function"
		
		logger.info(f"Handling query_database function call for query: {user_query[:50]}...")
		
		# Call the database query function
		result = query_database_for_relevant_chunks(user_query)
		
		logger.info(f"Database query completed, returned {len(result)} characters")
		return result
	else:
		logger.warning(f"Unknown function call: {name}")
		return f"Error: Unknown function '{name}'"
