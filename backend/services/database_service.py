import psycopg2
from config import DATABASE_URL

    # - `create_website(url, title, status)`
    # - `get_website(id)`
    # - `get_all_websites()`
    # - `update_website_status(id, status)`

#CRUD operations for websites
def create_website(url, title, status):
	try:
		conn = psycopg2.connect(DATABASE_URL)
		cursor = conn.cursor()

		cursor.execute("""
			INSERT INTO websites (url, title, status)
			VALUES (%s, %s, %s)
			RETURNING id;
		""", (url, title, status))
		conn.commit()
		website_id = cursor.fetchone()[0]
		cursor.close()
		conn.close()
		return website_id, None
	except Exception as e:
		return None, f"Error creating website: {e}"

def get_website(id):
	try:
		conn = psycopg2.connect(DATABASE_URL)
		cursor = conn.cursor()
		cursor.execute("""
			SELECT * FROM websites WHERE id = %s;

		""", (id,))
		website = cursor.fetchone()
		cursor.close()
		conn.close()
		return website, None
	except Exception as e:
		return None, f"Error getting website: {e}"

def get_all_websites():
	try:
		conn = psycopg2.connect(DATABASE_URL)
		cursor = conn.cursor()
		cursor.execute("""
			SELECT * FROM websites;
		""")
		websites = cursor.fetchall()
		cursor.close()
	except Exception as e:
		return None, f"Error getting all websites: {e}"

def update_website_status(id, status):
	try:
		conn = psycopg2.connect(DATABASE_URL)
		cursor = conn.cursor()
		cursor.execute("""
			UPDATE websites SET status = %s WHERE id = %s;
		""", (status, id))
		conn.commit()
		cursor.close()
		conn.close()
		return True, None
	except Exception as e:
		return False, f"Error updating website status: {e}"

#CRUD operations for content_chunks
    # - `create_chunk(website_id, chunk_text, chunk_index, embedding, metadata)`
    # - `get_chunks_by_website(website_id)`
    # - `get_chunk(id)`
# def create_chunk(website_id, chunk_text, chunk_indesx, embedding, meatadata):


	