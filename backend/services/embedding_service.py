from openai import OpenAI
from config import OPENAI_API_KEY
from typing import Optional
import logging
from functools import lru_cache
from services.database_service import get_db_cursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
if OPENAI_API_KEY:
	openai = OpenAI(api_key=OPENAI_API_KEY)
else:
	logger.error("OPENAI_API_KEY is not set")
	openai = None


def _get_embedding_from_db(text: str) -> Optional[list[float]]:
	"""
	Gets an embedding for the given text from the database.
	
	With register_vector() called in database_service, psycopg2 automatically
	converts PostgreSQL vector types to Python lists, so no parsing is needed.
	
	Args:
		text: The text to get an embedding for
	Returns:
		A list of floats representing the embedding, or None if not found
	"""
	if not text or not text.strip():
		return None
	
	try:
		with get_db_cursor() as cursor:
			cursor.execute("""
				SELECT embedding
				FROM content_chunks
				WHERE chunk_text = %s
				AND embedding IS NOT NULL
				LIMIT 1
			""", (text,))
			result = cursor.fetchone()
			if result and result[0] is not None:
				# register_vector() automatically converts PostgreSQL vector to Python list
				embedding = result[0]
				embedding = embedding.tolist()
				#logger.info(f"Embedding from database: {type(embedding)}, content: {embedding}")
				# Verify it's a list with expected dimension
				if isinstance(embedding, list) and len(embedding) == 1536:
					return embedding
				else:
					logger.warning(f"Unexpected embedding format or dimension: {type(embedding)}, length: {len(embedding) if isinstance(embedding, list) else 'N/A'}")
	except Exception as e:
		logger.warning(f"Error getting embedding from database: {e}")
	logger.info(f"no embedding found for text: {text}")
	return None

def _generate_embedding_from_api(text: str) -> Optional[list[float]]:
	"""
	Generates an embedding for the given text from the OpenAI API.
	
	Args:
		text: The text to generate an embedding for
	Returns:
		A list of floats representing the embedding, or None on error
	"""
	if openai is None:
		logger.error("OpenAI client is not initialized")
		return None
	
	if not text or not text.strip():
		logger.warning("Empty text provided for embedding generation")
		return None
	
	try:
		response = openai.embeddings.create(input=text, model="text-embedding-3-small")
		embedding = response.data[0].embedding
		# Verify embedding dimension (text-embedding-3-small should be 1536)
		if len(embedding) != 1536:
			logger.warning(f"Unexpected embedding dimension: {len(embedding)}, expected 1536")
		return embedding
	except Exception as e:
		logger.error(f"Error generating embedding: {e}")
		return None

@lru_cache(maxsize=1000)
def generate_embedding(text: str) -> Optional[list[float]]:
	"""
	Generates an embedding for the given text with caching.
	
	Caching strategy:
	1. Check @lru_cache (in-memory) - fastest
	2. Check database for existing embedding - persistent
	3. Generate new embedding via OpenAI API - slowest
	
	All results are cached by @lru_cache for future calls.
	
	Args:
		text: The text to generate an embedding for
	Returns:
		A list of floats representing the embedding (1536 dimensions),
		or None if generation fails or OpenAI client is not initialized
	"""
	if openai is None:
		logger.error("OpenAI client is not initialized")
		return None
	
	if not text or not text.strip():
		logger.warning("Empty or whitespace-only text provided")
		return None
	
	# Check database for existing embedding
	db_embedding = _get_embedding_from_db(text)
	if db_embedding is not None:
		logger.info("Using embedding from database")
		return db_embedding
	
	# Generate from API if not in database
	api_embedding = _generate_embedding_from_api(text)
	if api_embedding is not None:
		logger.info("Using embedding from API")
		return api_embedding
	
	logger.error(f"Failed to generate embedding for text")
	return None

def generate_embeddings_batch(texts: list[str]) -> Optional[list[list[float]]]:
	"""
	Generates embeddings for a list of texts.
	
	Uses generate_embedding() which has caching built-in. This means:
	- Cached embeddings (in-memory or database) are reused
	- Only uncached texts trigger API calls
	- Each text is processed individually to leverage caching
	
	Note: For better performance with many uncached texts, consider
	using OpenAI's batch API directly, but this approach maximizes
	cache hits and is simpler to maintain.
	
	Args:
		texts: A list of texts to generate embeddings for
	Returns:
		A list of lists of floats representing the embeddings,
		or None if OpenAI client is not initialized or empty input
	"""
	if openai is None:
		logger.error("OpenAI client is not initialized")
		return None
	
	if not texts:
		logger.warning("Empty texts list provided")
		return None
	
	results = []
	errors = []
	
	for i, text in enumerate(texts):
		if not text or not text.strip():
			logger.warning(f"Skipping empty text at index {i}")
			errors.append(i)
			continue
		
		embedding = generate_embedding(text)  # Uses @lru_cache internally
		if embedding is not None:
			results.append(embedding)
		else:
			logger.warning(f"Failed to generate embedding for text at index {i}")
			errors.append(i)
	
	if errors:
		logger.warning(f"Failed to generate embeddings for {len(errors)} out of {len(texts)} texts")
	
	# Return None only if all texts failed
	if len(results) == 0:
		logger.error("All embeddings failed to generate")
		return None
	
	return results

