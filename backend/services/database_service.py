import psycopg2
from config import DATABASE_URL
import logging
from contextlib import contextmanager
    # - `create_website(url, title, status)`
    # - `get_website(id)`
    # - `get_all_websites()`
    # - `update_website_status(id, status)`

#set up logging
logger = logging.getlogger(__name__)

# Connection pool created once and reused
_connection_pool = None

def get_connection_pool():
	"""Return a connection pool or create one
	to return if one doesn't already exist"""
	global _connection_pool 
	if _connection_pool is None:
		try:
			_connection_pool = psycopg2.pool.ThreadedConnectionPool(
				minconn=1, #min connections in pool
				maxconn=10, #max connections in pool
				dsn=DATABASE_URL,
			)
			logger.info("Database connection pool created")
		except Exception as e:
			logger.error(f"Error creating connection pool: {e}")
			raise
	return _connection_pool

@contextmanager
def get_db_connection():
	"""Context manager for database connections.
	Automatically returns connection to pool and handles errors.
	"""
	pool = get_connection_pool()
	conn = None
	try:
		conn = pool.getconn()
		yield conn #pauses this function to give conn to the caller
	except Exception as e:
		if conn:
			conn.rollback()
		logger.error(f"Database error: {e}")
		raise
	finally:
		#return the conn to the pool
		if conn:
			pool.putconn(conn)

@contextmanager
def get_db_cursor(commit=False):
	"""Context manager for database cursor.
	Automatically closes cursor and commits/rollbacks transaction.
	"""
	with get_db_connection() as conn:
		cursor = conn.cursor()
		try:
			yield cursor
			if commit:
				conn.commit()
			else:
				conn.rollback()
		except Exception as e:
			conn.rollback()
			raise
		finally:
			cursor.close()
#CRUD operations for websites
def create_website(url, title, status):
	"""Create a new website record"""
	try:
		with get_db_cursor(commit=True) as cursor:

			cursor.execute("""
				INSERT INTO websites (url, title, status)
				VALUES (%s, %s, %s)
				RETURNING id;
			""", (url, title, status))
			website_id = cursor.fetchone()[0]

			return website_id, None
	except Exception as e:
		logger.error(f"Error creating website: {e}")
		return None, f"Error creating website: {e}"

def get_website(id):
	"""Return website by id"""
	try:
		with get_db_cursor() as cursor:
			cursor.execute("""
				SELECT id, url, title, scraped_at, status, 
				FROM websites WHERE id = %s;
			""", (id,))
			website = cursor.fetchone()
			if not website:
				return None, "Website not found"
			website_data = {
				'id': website[0],
				'url': website[1],
				'title': website[2],
				'scraped_at': website[3],
				'status': website[4]
			}
			return website_data, None
	except Exception as e:
		logger.error(f"Error getting website: {e}")
		return None, f"Error getting website: {e}"

def get_all_websites():
	"""Get all websites."""
	try:
		with get_db_cursor() as cursor:
			cursor.execute("""
				SELECT id, url, title, scraped_at, status,
				FROM websites
				ORDER BY scraped_at DESC;
			""")
			websites = cursor.fetchall()
			if not websites:
				return None, "No websites found"
			website_data_list = []
			for w in websites:
				website_data_list.append(
					{
						'id': w[0],
						'url': w[1],
						'title': w[2],
						'scraped_at': w[3],
						'status': w[4]					
					}
				)
			return website_data_list, None
	except Exception as e:
		logger.error(f"Error getting all websites: {e}")
		return None, f"Error getting all websites: {e}"

def update_website_status(id, status):
	"""Update status of a website by id"""
	try:
		with get_db_cursor(True) as cursor:
			cursor.execute("""
				UPDATE websites SET status = %s WHERE id = %s;
			""", (status, id))
			#check to make sure that there is a website that got updated
			if cursor.rowcount == 0:
				return False, "Website not found"
			return True, None
	except Exception as e:
		logger.error(f"Error updating website status: {e}")
		return False, f"Error updating website status: {e}"

#CRUD operations for content_chunks
    # - `create_chunk(website_id, chunk_text, chunk_index, embedding, metadata)`
    # - `get_chunks_by_website(website_id)`
    # - `get_chunk(id)`
def create_chunk(website_id, chunk_text, chunk_index, embedding, metadata):
	"""Create a chunk record"""
	try:
		with get_db_cursor(commit=True) as cursor:
			cursor.execute("""
				INSERT INTO content_chunks (website_id, chunk_text, chunk_index, embedding, metadata)
				VALUES (%s, %s, %s, %s, %s)
				RETURNING id;
			""", (website_id, chunk_text, chunk_index, embedding, metadata))

			chunk_id = cursor.fetchone()[0]

			return chunk_id, None

	except Exception as e:
		logger.error(f"Error creating chunk: {e}")
		return None, f"Error creating chunk: {e}"

def get_chunks_by_website(website_id):
	"""Get all chunks for a website"""
	try:
		with get_db_cursor() as cursor:
			cursor.execute("""
				SELECT id, website_id, chunk_text, chunk_index, embedding, metadata,
				FROM content_chunks WHERE website_id = %s
				ORDER BY chunk_index;
			""", (website_id,))
			chunks = cursor.fetchall()
			if not chunks:
				return None, "No chunks found for this website"
			chunks_list = []
			for c in chunks:
				chunks_list.append(
					{
						'id': c[0],
						'website_id': c[1],
						'chunk_text': c[2],
						'chunk_index': c[3],
						'embedding': c[4],
						'metadata': c[5]
					}
				)

			return chunks_list, None
	except Exception as e:
		logger.error(f"Error getting chunks by website: {e}")
		return None, f"Error getting chunks by website: {e}"

def get_chunk(id):
	"""Get a chunk by id"""
	try:
		with get_db_cursor() as cursor:
			cursor.execute("""
				SELECT id, website_id, chunk_text, chunk_index, metadata, 
				FROM content_chunks WHERE id = %s;
			""", (id,))
			chunk = cursor.fetchone()
			if not chunk:
				return None, "Chunk not found"
			chunk_data = {
				'id': chunk[0],
				'website_id': chunk[1],
				'chunk_text': chunk[2],
				'chunk_index': chunk[3],
				'metadata': chunk[4]
			}
			return chunk_data, None
	except Exception as e:
		logger.error(f"Error getting chunk: {e}")
		return None, f"Error getting chunk: {e}"

#vector similarity search
def search_similar_chunks(query_embeddings, limit=5):
	try:
		with get_db_cursor() as cursor:
			""""Search for similar chunks using vector similarity"""
			# embedding_type = '[]'
			cursor.execute("""
				SELECT id, website_id, chunk_text, chunk_index, metadata,
				embedding <=> %s::vector as distance
				FROM content_chunks
				WHERE embedding IS NOT NULL
				ORDER BY embedding <=> %s::vector
				LIMIT %s;
			""", (query_embeddings, query_embeddings, limit))
			chunks = cursor.fetchall()
			if not chunks:
				return None, "No chunks found"
			chunks_list = []
			for c in chunks:
				chunks_list.append(
					{
						'id': c[0],
						'website_id': c[1],
						'chunk_text': c[2],
						'chunk_index': c[3],
						'metadata': c[4],
						'distance': float(c[5])
					}
				)
			return chunks, None
	except Exception as e:
		logger.error(f"Error searching similar chunks: {e}")
		return None, f"Error searching similar chunks: {e}"

#conversation/message storage
def save_message(conversation_id, message, sender):
	"""Save a message to the database"""
	try:
		with get_db_cursor(commit=True) as cursor:
			cursor.execute("""
				INSERT INTO messages (conversation_id, message, sender)
				VALUES (%s, %s, %s)
				RETURNING id;
			""", (conversation_id, message, sender))
			message_id = cursor.fetchone()[0]
			return message_id, None
	except Exception as e:
		logger.error(f"Error saving message: {e}")
		return False, f"Error saving message: {e}"

def get_conversation_history(conversation_id):
	"""Get all messages from a conversation"""
	try:
		with get_db_cursor() as cursor:
			cursor.execute("""
				SELECT id, conversation_id, message, sender, timestamp, 
				FROM messages 
				WHERE conversation_id = %s
				ORDER BY timestamp ASC;
			""", (conversation_id,))
			messages = cursor.fetchall()
			if not messages:
				return None, "No messages found for this conversation"
			messages_list = []
			for m in messages:
				messages_list.append(
					{
						'id': m[0],
						'conversation_id': m[1],
						'message': m[2],
						'sender': m[3],
						'timestamp': m[4]
					}
				)
			return messages_list, None
	except Exception as e:
		logger.error(f"Error getting conversation history: {e}")
		return None, f"Error getting conversation historyL {e}"
		
	#Cleanup function (call on application shutdown)
	def close_connection_pool():
		"""Close all connections in the pool"""
		global _connection_pool
		if _connection_pool:
			_connection_pool.closeall()
			_connection_pool = None
			logger.info("Database connection pool closed")