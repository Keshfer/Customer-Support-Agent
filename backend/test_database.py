import psycopg2
from config import DATABASE_URL

try:
	conn = psycopg2.connect(DATABASE_URL)
	cursor = conn.cursor()

	print("✓ Database connection successful!")
	
	cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
	result = cursor.fetchone()

	if result:
		print("✓ pgvector extension is installed!")
		print(f"{result}")
	else:
		print("X pgvector extension is not installed!")

	# Test vector type
	cursor.execute("SELECT typname FROM pg_type WHERE typname = 'vector';")
	vector_type = cursor.fetchone()
	if vector_type:
		print("✓ vector type is defined!")
		print(f"{vector_type}")
	else:
		print("X vector type is not defined!")

	#verifying tables
	cursor.execute("""
		SELECT table_name
		FROM information_schema.tables
		WHERE table_schema = 'public'
	""")

	tables = cursor.fetchall()
	print("Tabels in database:")
	# Should show: websites, content_chunks, messages
	for table in tables:
		print(f" * {table[0]}")

	#testing vector creation and usage (1536 for OpenAI embeddings)
	test_vector = [0.1] * 1536
	vector_str = '[' + ', '.join(map(str, test_vector)) + ']'
	#insert a vector
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS test_vectors (
			id SERIAL PRIMARY KEY,
			embedding vector(1536)
		);
	""")

	cursor.execute("""
		INSERT INTO test_vectors (embedding)
		VALUES (%s::vector);
	""", (vector_str,))
	conn.commit()

	#test vector similarity search (cosine similarity)
	cursor.execute("""
		SELECT embedding <=> %s::vector as distance
		FROM test_vectors
		LIMIT 1;
	""", (vector_str,))
	result = cursor.fetchone()
	print(f"✓ Vector operations work! Distance: {result[0]}")
	# Cleanup
	cursor.execute("DROP TABLE IF EXISTS test_vectors;")
	conn.commit()

	cursor.close()
	conn.close()

except Exception as e:
	print(f"X Error: {e}")