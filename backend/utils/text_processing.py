from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

"""- `chunk_text(text, chunk_size=800, overlap=100)` - Split text into chunks
`count_tokens(text)` - Approximate token counting

"""

def chunk_text(text, chunk_size=800, overlap=100):
	"""Split text into chunks at fixed sizes with overlap"""
	#https://docs.langchain.com/oss/python/integrations/splitters/split_by_token
	chunks = []
	splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
		encoding_name="cl100k_base",
		chunk_size=chunk_size, 
		chunk_overlap=overlap)
	chunks = splitter.split_text(text)
	return chunks
	#for i in range(i, len(text), chunk_size - overlap):

def count_tokens(text):
	"""Count tokens of text"""
	count = len(tiktoken.get_encoding("cl100k_base").encode(text))
	return count