# List of tools available to the agent
tools = [
	{
		"type": "function",
		"name": "website_search",
		"description": "Scrape the website and store the information",
		"parameters": {
			"type": "object",
			"properties": {
				"website_url": { "type": "string", "description": "The URL of the website to search" },
			},
			"required": ["website_url"],
		},
	},
	{
		"type": "function",
		"name": "query_database",
		"description": "Search the database for relevant content",
		"parameters": {
			"type": "object",
			"properties": {
				"db_query": { "type": "string", "description": "The query used to find relevant content to pull from the database"},
			},
			"required": ["db_query"],
		},
	},
]

def format_chat_prompt():
	"""
	Returns the system prompt (instructions) for the customer support AI agent.
	
	This function returns only the system prompt/instructions. The conversation history
	is passed separately to the OpenAI API via the 'input' parameter in openai_service.py.
	
	Returns:
		A string representing the system prompt/instructions for the AI agent
	"""
	return """You are a helpful customer support AI agent with a strong focus on accuracy and helpfulness.
Your role is to answer questions based on the information fetched from your database.

Guidelines:
- Only answer questions based on the information fetched from your database.
- If you can't find the relevant information, politely say you don't have that information.
- Prompt the user to provide the relevant information through a website link if the answer is not in the context.
- Be concise and helpful.
- Use the tools available to you to satisfy the above guidelines."""
def format_scraping_confirmation_prompt(website_title):
	"""
	Formats the scraping confirmation prompt for the OpenAI API
	Args:
		website_title: The title of the website that was scraped
	Returns:
		A string representing the formatted prompt
	"""
	return f"""You have successfully scraped the website: {website_title}.
Notify the user that the website has been scraped and you're ready to answer questions about its content."""
