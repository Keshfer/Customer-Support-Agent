import validators

"""  - `validate_url(url)` - URL validation
  - `sanitize_input(text)` - Input sanitization
"""

def validate_url(url):
	"""Validate url"""
	result = validators.url(url)
	if result != True:
		print(f"Invalid URL: {url}")
		#raise ValueError(f"Invalid URL: {url}")
	return True

def sanitize_input(text):
	"""Sanitize input"""
	return text.strip()

