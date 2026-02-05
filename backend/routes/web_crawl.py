"""
Website Scraping Routes

This module provides Flask routes for website scraping functionality:
- POST /api/websites/scrape: Scrape a website and store its content
- GET /api/websites/url: Get website details and chunks by URL
- GET /api/websites/title: Get website details and chunks by title

All endpoints include request validation and comprehensive error handling.
"""

import datetime
import json
from flask import Blueprint, jsonify, request
from backend.services.database_service import (
	create_chunk_by_url, 
	create_website, 
	update_website_status_by_url,
	update_website_title_by_url,
	get_website_by_url,
	get_website_by_title,
	get_chunks_by_website_url
)
from backend.services.scraping_service import scrape_website, process_scraped_content
from backend.services.embedding_service import generate_embeddings_batch
from backend.utils.validate import validate_url
import logging
from werkzeug.exceptions import HTTPException, UnsupportedMediaType


# Set up logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Flask blueprint instance for website crawling routes
# Blueprints allow us to organize routes into logical groups
crawl_bp = Blueprint('crawl_route', __name__)


def scrape_and_store_website(url: str) -> dict:
	"""
	Helper function that handles the complete website scraping workflow.
	
	This function performs:
	1. Validates the URL format
	2. Checks if website already exists (avoids duplicate scraping)
	3. Creates or updates website record with 'pending' status
	4. Scrapes website content using Firecrawl API
	5. Processes and chunks the content
	6. Generates embeddings for semantic search
	7. Stores chunks with embeddings in database
	8. Updates website status to 'completed'
	
	Args:
		url: The URL of the website to scrape (must be a valid URL string)
	
	Returns:
		A dictionary with the following structure:
		
		Success (200):
		{
			'success': True,
			'status_code': 200,
			'message': 'Website scraped and chunks stored successfully',
			'website': {...},  # Website data dict
			'chunks_count': 5
		}
		
		Success - Already exists (200):
		{
			'success': True,
			'status_code': 200,
			'website': {...},  # Existing website data
			'chunks_count': 0  # Not counted if already exists
		}
		
		Success - No content (200):
		{
			'success': True,
			'status_code': 200,
			'message': 'Website scraped successfully but has no content to chunk',
			'website': {...},
			'chunks_count': 0
		}
		
		Error - Invalid URL (400):
		{
			'success': False,
			'status_code': 400,
			'error': 'Invalid URL: <error message>'
		}
		
		Error - Scraping failed (500):
		{
			'success': False,
			'status_code': 500,
			'error': '<error message>'
		}
		
		Error - Processing failed (500):
		{
			'success': False,
			'status_code': 500,
			'error': '<error message>',
			'total_chunks': 10,  # Optional: if chunking/embedding failed
			'failed_chunks': 2   # Optional: if storage failed
		}
	"""
	try:
		# Step 1: Validate URL format
		# Uses validators library to check URL format and scheme (http/https)
		url_valid, error_message = validate_url(url)
		if not url_valid:
			logger.warning(f"Invalid URL provided: {url} - {error_message}")
			return {
				'success': False,
				'status_code': 400,
				'error': f'Invalid URL: {error_message}'
			}

		# Step 2: Check if website already exists in database
		# If website exists and is completed, return existing data to avoid duplicate scraping
		existing_website, _ = get_website_by_url(url)
		if existing_website and existing_website['status'] == 'completed':
			logger.info(f"Website already exists and is completed: {url}")
			return {
				'success': True,
				'status_code': 200,
				'website': existing_website
			}
		
		# Step 3: Create or update website record
		# If website exists but not completed (pending/failed), update status to pending
		# If website doesn't exist, create new record with 'pending' status
		if existing_website:
			# Update existing website status to 'pending' for re-scraping
			logger.info(f"Updating existing website status to 'pending': {url}")
			success, error = update_website_status_by_url(url, "pending")
			if error:
				logger.error(f"Failed to update website status: {error}")
				return {
					'success': False,
					'status_code': 500,
					'error': error
				}
		else:
			# Create new website record with 'pending' status
			# Title is set to None initially, will be updated after scraping
			logger.info(f"Creating new website record: {url}")
			website_id, error = create_website(url, None, "pending")
			if error:
				logger.error(f"Failed to create website record: {error}")
				return {
					'success': False,
					'status_code': 500,
					'error': error
				}

		# Step 4: Scrape website content using Firecrawl API
		# This calls the scraping service which handles Firecrawl API integration
		logger.info(f"Starting website scraping: {url}")
		content_json = scrape_website(url)
		
		# Check if scraping failed
		if 'error' in content_json:
			logger.error(f"Scraping failed: {content_json['error']}")
			# Update website status to 'failed' to indicate scraping failure
			update_website_status_by_url(url, "failed")
			return {
				'success': False,
				'status_code': 500,
				'error': content_json['error']
			}
		
		# Extract scraped content and metadata
		website_title = content_json.get('website_title', 'Untitled')
		markdown_content = content_json.get('markdown_content', '')
		scraped_at = datetime.datetime.now().isoformat()
		
		logger.info(f"Successfully scraped website: {url}, title: {website_title}")
		
		# Step 5: Update website record with actual title from scraping
		# Title was None initially, now we update it with the scraped title
		success, error = update_website_title_by_url(url, website_title)
		if error:
			logger.warning(f"Failed to update website title (non-critical): {error}")
		
		# Step 6: Process and chunk the scraped content
		# Chunk size: 800 tokens, overlap: 100 tokens for context preservation
		# This splits the content into manageable pieces for embedding and storage
		logger.info(f"Processing and chunking content for: {url}")
		
		# Handle empty content case - if content is empty, we still create the website record
		# but mark it as completed with no chunks (some websites may have no text content)
		if not markdown_content or markdown_content.strip() == '':
			logger.warning(f"Website has no content to chunk: {url}")
			# Update status to completed even with no chunks
			update_website_status_by_url(url, "completed")
			website_data, _ = get_website_by_url(url)
			return {
				'success': True,
				'status_code': 200,
				'message': 'Website scraped successfully but has no content to chunk',
				'website': website_data,
				'chunks_count': 0
			}
		
		chunks = process_scraped_content(markdown_content, chunk_size=800, overlap=100)
		
		# Validate that chunking was successful
		# If chunking fails but we have content, that's an error
		if chunks is None or len(chunks) == 0:
			logger.error(f"Failed to chunk content for: {url} (content exists but chunking failed)")
			update_website_status_by_url(url, "failed")
			return {
				'success': False,
				'status_code': 500,
				'error': 'Failed to chunk content'
			}
		
		logger.info(f"Content chunked into {len(chunks)} pieces")
		
		# Step 7: Generate embeddings for all chunks
		# Embeddings are vector representations used for semantic search
		# Batch processing is more efficient than individual API calls
		logger.info(f"Generating embeddings for {len(chunks)} chunks")
		embeddings = generate_embeddings_batch(chunks)
		
		if embeddings is None or len(embeddings) != len(chunks):
			logger.error(f"Failed to generate embeddings or count mismatch for: {url}")
			update_website_status_by_url(url, "failed")
			return {
				'success': False,
				'status_code': 500,
				'error': 'Failed to generate embeddings'
			}
		
		logger.info(f"Successfully generated {len(embeddings)} embeddings")
		
		# Step 8: Store chunks with embeddings in database
		# Each chunk is stored with its embedding and metadata
		# Metadata includes title, URL, and scraped timestamp for reference
		error_count = 0
		for i, chunk in enumerate(chunks):
			# Prepare metadata for this chunk
			# Metadata is stored as JSONB in PostgreSQL for flexible querying
			metadata = {
				'title': website_title,
				'url': url,
				'scraped_at': scraped_at,
				'chunk_index': i
			}
			
			# Store chunk with embedding in database
			# create_chunk_by_url handles the URL to website_id lookup internally
			chunk_id, error = create_chunk_by_url(
				url, 
				chunk, 
				i, 
				embeddings[i], 
				json.dumps(metadata)  # Convert dict to JSON string for JSONB storage
			)
			
			if error:
				logger.error(f"Error creating chunk {i}: {error}")
				error_count += 1
		
		# If any chunks failed to store, mark website as failed
		if error_count > 0:
			logger.warning(f"Failed to store {error_count} out of {len(chunks)} chunks")
			update_website_status_by_url(url, "failed")
			return {
				'success': False,
				'status_code': 500,
				'error': f'Failed to store {error_count} chunks',
				'total_chunks': len(chunks),
				'failed_chunks': error_count
			}
		
		logger.info(f"Successfully stored {len(chunks)} chunks in database")
		
		# Step 9: Update website status to 'completed'
		# This indicates the scraping and storage process completed successfully
		success, error = update_website_status_by_url(url, "completed")
		if error:
			logger.warning(f"Failed to update website status (non-critical): {error}")
		
		# Step 10: Retrieve final website data and return response
		# Get the complete website record including all updated fields
		website_data, _ = get_website_by_url(url)
		
		logger.info(f"Website scraping completed successfully: {url}")
		
		return {
			'success': True,
			'status_code': 200,
			'message': 'Website scraped and chunks stored successfully',
			'website': website_data,
			'chunks_count': len(chunks)
		}
	except Exception as e:
		# Catch any unexpected errors and return generic error message
		# Log the full error for debugging while keeping response user-friendly
		logger.error(f"Unexpected error scraping website: {e}", exc_info=True)
		return {
			'success': False,
			'status_code': 500,
			'error': 'An unexpected error occurred while scraping the website'
		}


@crawl_bp.route('/websites/scrape', methods=['POST'])
def scrape_website_endpoint():
	"""
	Scrape a website and store its content in the database.
	
	This endpoint handles the HTTP request/response and delegates the actual
	scraping logic to scrape_and_store_website() helper function.
	
	Request Body:
		{
			"url": "https://example.com"  # Required: URL to scrape
		}
	
	Returns:
		Success (200): {
			"message": "Website scraped and chunks stored successfully",
			"website": {
				"id": 1,
				"url": "https://example.com",
				"title": "Example Website",
				"status": "completed",
				...
			},
			"chunks_count": 5
		}
		
		Error (400): Invalid URL or missing URL in request
		Error (500): Scraping, processing, or database errors
	
	Raises:
		HTTPException: Re-raised for proper Flask error handling
		Exception: Catches all other exceptions and returns 500 error
	"""
	try:
		# Step 1: Extract and validate request data
		# Get JSON data from request body
		data = request.get_json()
		# Validate that request contains JSON data with 'url' field
		if 'url' not in data:
			return jsonify({'error': 'URL is required in request body'}), 400
		
		# Extract and clean URL (remove leading/trailing whitespace)
		url = data['url'].strip()
		if not url:
			return jsonify({'error': 'URL cannot be empty'}), 400
		
		logger.info(f"Received scrape request for URL: {url}")
		
		# Step 2: Call helper function to perform scraping
		# The helper function handles all validation, scraping, processing, and storage
		result = scrape_and_store_website(url)
		
		# Step 3: Convert result dict to Flask response
		status_code = result.get('status_code', 500)
		
		# Build response based on success/failure
		if result.get('success', False):
			# Success case - build response with available fields
			response_data = {}
			if 'message' in result:
				response_data['message'] = result['message']
			if 'website' in result:
				response_data['website'] = result['website']
			if 'chunks_count' in result:
				response_data['chunks_count'] = result['chunks_count']
			return jsonify(response_data), status_code
		else:
			# Error case - return error message
			error_data = {'error': result.get('error', 'An unknown error occurred')}
			# Include additional error details if available
			if 'total_chunks' in result:
				error_data['total_chunks'] = result['total_chunks']
			if 'failed_chunks' in result:
				error_data['failed_chunks'] = result['failed_chunks']
			return jsonify(error_data), status_code
			
	except HTTPException:
		raise
	except Exception as e:
		# Catch any unexpected errors and return generic error message
		# Log the full error for debugging while keeping response user-friendly
		logger.error(f"Unexpected error in scrape_website_endpoint: {e}", exc_info=True)
		return jsonify({'error': 'An unexpected error occurred while scraping the website'}), 500


@crawl_bp.route('/websites/title', methods=['GET'])
def get_website_by_title_endpoint():
	"""
	Get website details and associated chunks by title.
	
	This endpoint retrieves a website record and all its content chunks
	using the website title as the identifier. If multiple websites have
	the same title, returns the most recently scraped one.
	
	Request Body:
		{
			"title": "Example Website"  # Required: Title of the website to retrieve
		}
	
	Returns:
		Success (200): {
			"website": {
				"id": 1,
				"url": "https://example.com",
				"title": "Example Website",
				"status": "completed",
				"scraped_at": "2024-01-01T00:00:00",
				...
			},
			"chunks": [
				{
					"id": 1,
					"chunk_text": "...",
					"chunk_index": 0,
					"metadata": {...},
					...
				},
				...
			],
			"chunks_count": 5
		}
		
		Error (400): Missing or invalid title parameter
		Error (404): Website not found
		Error (500): Database error
	
	Raises:
		Exception: Catches all exceptions and returns 500 error
	"""
	# Step 1: Extract and validate title from request body
	# Note: Using request body for GET is non-standard but allows for complex queries
	# GET requests typically use query parameters, but this approach is acceptable
	try:
		# Attempt to get JSON data from request body
		# Use silent=True to return None instead of raising exception for invalid Content-Type
		# This allows us to handle the error gracefully
		data = request.get_json(silent=True)
		
		# Check if JSON parsing failed (None indicates no JSON or invalid Content-Type)
		if data is None:
			# Check if the request has a Content-Type header
			content_type = request.content_type
			if content_type and 'application/json' not in content_type:
				# Invalid Content-Type header
				return jsonify({'error': 'Content-Type must be application/json'}), 415
			else:
				# No Content-Type or missing request body
				return jsonify({'error': 'Request body is required and must be valid JSON'}), 400
		
		# Validate that request contains JSON data with 'title' field
		if 'title' not in data:
			return jsonify({'error': 'Title is required in request body'}), 400
		
		# Extract and clean title (remove leading/trailing whitespace)
		title = data['title'].strip()
		if not title:
			return jsonify({'error': 'Title cannot be empty'}), 400
		
		logger.info(f"Retrieving website by title: {title}")
		
		# Step 2: Retrieve website from database by title
		# get_website_by_title returns the most recently scraped website if multiple exist
		website, error = get_website_by_title(title)
		
		if error or not website:
			logger.warning(f"Website not found with title: {title}")
			return jsonify({'error': 'Website not found'}), 404
		
		# Step 3: Retrieve all chunks associated with this website
		# Use the URL from the website data to get chunks
		# get_chunks_by_website_url returns (chunks_list, error) tuple
		website_url = website['url']
		chunks, chunks_error = get_chunks_by_website_url(website_url)
		
		# Handle chunks retrieval - if error occurs, return empty chunks list
		# This allows the endpoint to return website data even if chunks can't be retrieved
		if chunks_error:
			logger.warning(f"Error retrieving chunks for {website_url}: {chunks_error}")
			chunks = []  # Return empty chunks list instead of failing completely
		elif chunks is None:
			# No chunks found is not an error, just return empty list
			chunks = []
		
		logger.info(f"Retrieved website and {len(chunks) if chunks else 0} chunks for title: {title}")
		
		# Step 4: Return website data with chunks
		# Include chunks_count for consistency with scrape endpoint response format
		return jsonify({
			'website': website,
			'chunks': chunks if chunks else [],
			'chunks_count': len(chunks) if chunks else 0
		}), 200
	except HTTPException as e:
		# Catch HTTP exceptions (like 415 Unsupported Media Type) and return them properly
		# This handles cases where Flask/Werkzeug raises HTTP exceptions
		logger.warning(f"HTTP exception in get_website_by_title_endpoint: {e.code} - {e.description}")
		return jsonify({'error': e.description}), e.code
	except Exception as e:
		# Catch any unexpected errors and return generic error message
		# Log the full error for debugging while keeping response user-friendly
		logger.error(f"Unexpected error getting website by title: {e}", exc_info=True)
		return jsonify({'error': 'An unexpected error occurred while getting website by title'}), 500

@crawl_bp.route('/websites/url', methods=['GET'])
def get_website_by_url_endpoint():
	"""
	Get website details and associated chunks by URL.
	
	This endpoint retrieves a website record and all its content chunks
	using the website URL as the identifier.
	
	Request Body:
		{
			"url": "https://example.com"  # Required: URL of the website to retrieve
		}
	
	Returns:
		Success (200): {
			"website": {
				"id": 1,
				"url": "https://example.com",
				"title": "Example Website",
				"status": "completed",
				"scraped_at": "2024-01-01T00:00:00",
				...
			},
			"chunks": [
				{
					"id": 1,
					"chunk_text": "...",
					"chunk_index": 0,
					"metadata": {...},
					...
				},
				...
			],
			"chunks_count": 5
		}
		
		Error (400): Missing or invalid URL parameter
		Error (404): Website not found
		Error (500): Database error
	
	Raises:
		Exception: Catches all exceptions and returns 500 error
	"""
	# Step 1: Extract and validate URL from request body
	# Note: Using request body for GET is non-standard but allows for complex queries
	# GET requests typically use query parameters, but this approach is acceptable

	try:
		# Attempt to get JSON data from request body
		# Use silent=True to return None instead of raising exception for invalid Content-Type
		# This allows us to handle the error gracefully
		data = request.get_json(silent=True)
		
		# Check if JSON parsing failed (None indicates no JSON or invalid Content-Type)
		if data is None:
			# Check if the request has a Content-Type header
			content_type = request.content_type
			if content_type and 'application/json' not in content_type:
				# Invalid Content-Type header
				return jsonify({'error': 'Content-Type must be application/json'}), 415
			else:
				# No Content-Type or missing request body
				return jsonify({'error': 'Request body is required and must be valid JSON'}), 400
		
		# Validate that request contains JSON data with 'url' field
		if 'url' not in data:
			return jsonify({'error': 'URL is required in request body'}), 400
		
		# Extract and clean URL (remove leading/trailing whitespace)
		url = data['url'].strip()
		if not url:
			return jsonify({'error': 'URL cannot be empty'}), 400
		
		logger.info(f"Retrieving website by URL: {url}")
		
		# Step 2: Validate URL format
		# Ensure the URL is in a valid format before querying database
		url_valid, error_message = validate_url(url)
		if not url_valid:
			logger.warning(f"Invalid URL format provided: {url} - {error_message}")
			return jsonify({'error': f'Invalid URL format: {error_message}'}), 400
		
		# Step 3: Retrieve website from database
		# get_website_by_url returns (website_data, error) tuple
		website, error = get_website_by_url(url)
		
		if error or not website:
			logger.warning(f"Website not found: {url}")
			return jsonify({'error': 'Website not found'}), 404
		
		# Step 4: Retrieve all chunks associated with this website
		# Chunks are ordered by chunk_index for proper sequence
		# get_chunks_by_website_url returns (chunks_list, error) tuple
		chunks, chunks_error = get_chunks_by_website_url(url)
		
		# Handle chunks retrieval - if error occurs, return empty chunks list
		# This allows the endpoint to return website data even if chunks can't be retrieved
		if chunks_error:
			logger.warning(f"Error retrieving chunks for {url}: {chunks_error}")
			chunks = []  # Return empty chunks list instead of failing completely
		elif chunks is None:
			# No chunks found is not an error, just return empty list
			chunks = []
		
		logger.info(f"Retrieved website and {len(chunks) if chunks else 0} chunks for: {url}")
		
		# Step 5: Return website data with chunks
		# Include chunks_count for consistency with scrape endpoint response format
		return jsonify({
			'website': website,
			'chunks': chunks if chunks else [],
			'chunks_count': len(chunks) if chunks else 0
		}), 200
	
	except HTTPException as e:
		# Catch HTTP exceptions (like 415 Unsupported Media Type) and return them properly
		# This handles cases where Flask/Werkzeug raises HTTP exceptions
		logger.warning(f"HTTP exception in get_website_by_url_endpoint: {e.code} - {e.description}")
		return jsonify({'error': e.description}), e.code
	except Exception as e:
		# Catch any unexpected errors and return generic error message
		# Log the full error for debugging while keeping response user-friendly
		logger.error(f"Unexpected error getting website by URL: {e}", exc_info=True)
		return jsonify({'error': 'An unexpected error occurred while getting website by URL'}), 500