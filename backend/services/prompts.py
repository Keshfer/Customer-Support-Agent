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
		"description": "Search the database for relevant content that can answer the user's query. Use this when you need to find information from previously scraped websites.",
		"parameters": {
			"type": "object",
			"properties": {
				"user_query": { "type": "string", "description": "The user's query you are trying to answer"},
			},
			"required": ["user_query"],
		},
	},
]

def format_chat_prompt(relevant_info: str):
	"""
	Returns the system prompt (instructions) for the customer support AI agent.
	
	This function returns only the system prompt/instructions. The conversation history
	is passed separately to the OpenAI API via the 'input' parameter in openai_service.py.
	
	Returns:
		A string representing the system prompt/instructions for the AI agent
	"""
	return """You are a helpful customer support AI agent with a strong focus on accuracy and helpfulness.
Your role is to answer user questions based on the information gatherd from websites the user provides.
Respond in a human friendly Markdown format. Don't reply in a JSON format unless appropriate for the user's question.

Guidelines:
- Use the tools available to you to find information and answer user questions.
	*Function call results are found in the output field of the type function_call_output.
- If you need information from the database, use the query_database tool with the user's question.
- If you need to scrape a website, use the website_search tool with the website URL.
- Only answer questions based on information you retrieve using the available tools.
- If you cannot find enough information to answer the question, let the user know and suggest they provide a website link for you to examine.
- Do not make up information. If you don't have the information, say so.
- Be concise and helpful.
- You can make multiple tool calls in sequence if needed to gather all necessary information. However, you only
have a limited number of iterations to call tools and reason before you must return a final response to the user.
- At the final iteration, you must generate a final response for the user.

Relevant Info:
{relevant_info}
"""

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
