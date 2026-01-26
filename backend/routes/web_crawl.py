#   - `POST /api/websites/scrape`:
#     - Validate URL
#     - Check if website already exists
#     - Create website record with 'pending' status
#     - Call scraping_service to fetch content
#     - Process and chunk content
#     - Store chunks with their embeddings in database (embedding column in content_chunks table)
#     - Store chunks in database
#     - Update website status to 'completed'
#     - Generate LLM confirmation message
#     - Return response with website_id and LLM message
#   - `GET /api/websites`:
#     - Return list of all scraped websites
#   - `GET /api/websites/:id`:
#     - Return website details and associated chunks

from crypt import methods
import datetime
from flask import Blueprint, jsonify, request
from backend.services.database_service import create_chunk, create_website
from backend.services.scraping_service import scrape_website, process_scraped_content
from backend.services.embedding_service import generate_embedding, generate_embeddings_batch
from backend.utils.validate import validate_url
import logging
from backend.services.database_service import update_website_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#create a blueprint instance
crawl_bp = Blueprint('crawl_route', __name__)

@crawl_bp.route('websites/scrape', methods=['POST'])
def scrap_website():
	"""
	Scrape a website and store its content in the database.
	
	Flow:
	1. Validate URL
	2. Check if website already exists
	3. Create website record with 'pending' status (title=None or domain)
	4. Scrape website to get title and content
	5. Update website record with actual title
	6. Process and chunk content
	7. Generate embeddings for chunks
	8. Store chunks with embeddings in database
	9. Update website status to 'completed'
	10. Create confirmation message
	11. Return response
	"""
	try:
		#Get URL from request body
		data = request.get_json()
		if not data or 'url' not in data:
			return jsonify({'error': 'URL is required'}), 400
		url = data['url'].strip()
		logger.info(f"Scraping website: {url}")
		#validate url
		url_valid, _ = validate_url(url)
		if not url_valid:
			return jsonify({'error': 'Invalid URL'}), 400

		#create website record with 'pending' status
		website_id, error = create_website(url, None, "pending")
		if error:
			return jsonify({'error': error}), 500

		#call scraping_service to fetch content
		content_json = scrape_website(url)
		if 'error' in content_json:
			return jsonify({'error': content_json['error']}), 500
		website_title = content_json['website_title']
		markdown_content = content_json['markdown_content']
		scraped_at = datetime.now().isoformat()
		#update website record with actual title
		status, error = update_website_status(website_id, "completed")
		if error:
			return jsonify({'error': error}), 500

		#chunk content
		chunks =  process_scraped_content(markdown_content, chunk_size=800, overlap=100)
		if chunks is None:
			return jsonify({'error': 'Failed to chunk content'}), 500

		#generate embeddings for chunks
		embeddings = generate_embeddings_batch(chunks)
		if embeddings is None:
			return jsonify({'error': 'Failed to generate embeddings'}), 500
		#store chunks with embeddings in database
		error_count = 0
		for i, chunk in enumerate(chunks):
			metadata = {
				'title': website_title,
				'url': url,
				'scraped_at': scraped_at
			}
			chunk_id, error = create_chunk(website_id, chunk, i, embeddings[i], metadata)
			if error:
				logger.error(f"Error creating chunk: {error}")
				error_count += 1
		if error_count > 0:
			return jsonify({'error': f'Failed to store {error_count} chunks'}), 500
		else:
			return jsonify({'message': 'Website scraped and chunks stored successfully'}), 200
	except Exception as e:
		logger.error(f"Error scraping website: {e}")
		return jsonify({'error': 'Failed to scrape website'}), 500


