# pip install firecrawl-py
import time
from typing import Optional
from firecrawl import Firecrawl
from config import FIRECRAWL_API_KEY
from utils.text_processing import chunk_text
from utils.validate import validate_url
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firecrawl client
if FIRECRAWL_API_KEY:
	firecrawl = Firecrawl(api_key=FIRECRAWL_API_KEY)
else:
	logger.error("FIRECRAWL_API_KEY is not set")
	firecrawl = None

# scrape a website
def scrape_website(url: str, attempts: int = 3) -> Optional[dict]:
	"""
	Scrapes a website page and returns the title and markdown content
	Args:
		url: The URL of the website to scrape
		attempts: The number of attempts to scrape the website page
	Returns:
		A dictionary with the website title and markdown content
	"""
	if firecrawl is None:
		logger.error("Firecrawl client is not initialized")
		return {"error": "Firecrawl client is not initialized"}
	counter = 0
	url_valid, message = validate_url(url)
	if not url_valid:
		return {"error": message}
	while counter < attempts:
		try:
			#default timeout is 3000 ms or 30 seconds
			doc = firecrawl.scrape(url, formats=["markdown"])
			#logger.info(doc)
			if doc.markdown is not None and doc.markdown != "":
				markdown_content = doc.markdown
			else:
				markdown_content = "no content found"
			if doc.metadata.title is not None and doc.metadata.title != "":
				website_title = doc.metadata.title
			else:
				website_title = "no title found"
			return_json = {
				"website_title": website_title,
				"markdown_content": markdown_content,
			}
			return return_json

		except Exception as e:
			logger.error(f"Error scraping website: {e}")
			counter += 1
			time.sleep(1)
	return {"error": "Failed to scrape website after 3 attempts"}

def process_scraped_content(content: str, chunk_size: int = 800, overlap: int = 100) -> Optional[list[str]]:
	"""
	Processes the scraped content and returns a list of chunks
	Args:
		content: The content to process
		chunk_size: The size of each chunk
		overlap: The overlap between chunks
	Returns:
		A list of chunks
	"""
	try:

		chunks = chunk_text(content, chunk_size, overlap)
		return chunks
	except Exception as e:
		logger.error(f"Error processing scraped content: {e}")
		return {"error": "Failed to process scraped content"}
