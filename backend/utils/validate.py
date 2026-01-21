import validators
#from validators import url
from markupsafe import escape
import re
from urllib.parse import urlparse
from typing import Optional
"""  - `validate_url(url)` - URL validation
  - `sanitize_input(text)` - Input sanitization
"""

def validate_url(url) -> tuple[bool, Optional[str]]:
	"""Validate url"""
	
	result = validators.url(url)
	if result != True:
		print(f"Invalid URL: {url}")
		return (False, f"Invalid URL: {url}")
		#raise ValueError(f"Invalid URL: {url}")
	parsed_url = urlparse(url)
	if parsed_url.scheme not in ['http', 'https']:
		#print(f"Invalid URL: {url}")
		return (False, f"Invalid URL: {url}")
	return (True, None)

def sanitize_input(text):
	"""Sanitize input"""
	safe_text = escape(text)
	#print(safe_text)
	#safe_text = re.sub(r'[^\w\s]', '', safe_text)
	return safe_text.strip()

