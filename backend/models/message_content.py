"""
Message Content Models

This module provides standardized classes for message content structures:
- MessageContent: Represents a regular message with content and show_user flag
- FunctionCallOutput: Represents a function call output with call_id, output, and show_user flag

These classes manage their own internal dictionary structure and provide methods
to convert to/from JSON and OpenAI-compatible formats.
"""

from typing import Dict, Any, Optional
import json


class MessageContent:
	"""
	Standardized class for message content.
	
	Structure:
		{
			"type": "message",
			"content": str,  # The message text
			"show_user": bool  # Whether to display to user
		}
	"""
	
	def __init__(self, content: str, show_user: bool = True):
		"""
		Initialize a MessageContent instance.
		
		Args:
			content: The message text content
			show_user: Whether this message should be displayed to the user (default: True)
		"""
		self.content = content
		self.show_user = show_user
	
	def to_dict(self) -> Dict[str, Any]:
		"""
		Convert to dictionary format for database storage.
		
		Returns:
			Dictionary with type, content, and show_user keys
		"""
		return {
			"type": "message",
			"content": self.content,
			"show_user": self.show_user
		}
	
	def to_json(self) -> str:
		"""
		Convert to JSON string for database storage.
		
		Returns:
			JSON string representation
		"""
		return json.dumps(self.to_dict())
	
	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'MessageContent':
		"""
		Create MessageContent instance from dictionary.
		
		Args:
			data: Dictionary with type, content, and show_user keys
			
		Returns:
			MessageContent instance
		"""
		return cls(
			content=data.get("content", ""),
			show_user=data.get("show_user", True)
		)
	
	@classmethod
	def from_json(cls, json_str: str) -> 'MessageContent':
		"""
		Create MessageContent instance from JSON string.
		
		Args:
			json_str: JSON string representation
			
		Returns:
			MessageContent instance
		"""
		data = json.loads(json_str)
		return cls.from_dict(data)
	
	def to_openai_content(self) -> str:
		"""
		Convert to OpenAI-compatible format (just the content string).
		Removes show_user and type fields as OpenAI doesn't support them.
		
		Returns:
			The MessageContent as a JSON formatted string
		"""
		return self.to_json()


class FunctionCallOutput:
	"""
	Standardized class for function call output content.
	
	Structure:
		{
			"type": "function_call_output",
			"call_id": str,  # The function call ID
			"output": str,  # The function call result/output
			"show_user": bool  # Whether to display to user (default: False)
		}
	"""
	
	def __init__(self, call_id: str, output: str, show_user: bool = False):
		"""
		Initialize a FunctionCallOutput instance.
		
		Args:
			call_id: The function call ID
			output: The function call result/output
			show_user: Whether this output should be displayed to the user (default: False)
		"""
		self.call_id = call_id
		self.output = output
		self.show_user = show_user
	
	def to_dict(self) -> Dict[str, Any]:
		"""
		Convert to dictionary format for database storage.
		
		Returns:
			Dictionary with type, call_id, output, and show_user keys
		"""
		return {
			"type": "function_call_output",
			"call_id": self.call_id,
			"output": self.output,
			"show_user": self.show_user
		}
	
	def to_json(self) -> str:
		"""
		Convert to JSON string for database storage.
		
		Returns:
			JSON string representation
		"""
		return json.dumps(self.to_dict())
	
	@classmethod
	def from_dict(cls, data: Dict[str, Any]) -> 'FunctionCallOutput':
		"""
		Create FunctionCallOutput instance from dictionary.
		
		Args:
			data: Dictionary with type, call_id, output, and show_user keys
			
		Returns:
			FunctionCallOutput instance
		"""
		return cls(
			call_id=data.get("call_id", ""),
			output=data.get("output", ""),
			show_user=data.get("show_user", False)
		)
	
	@classmethod
	def from_json(cls, json_str: str) -> 'FunctionCallOutput':
		"""
		Create FunctionCallOutput instance from JSON string.
		
		Args:
			json_str: JSON string representation
			
		Returns:
			FunctionCallOutput instance
		"""
		data = json.loads(json_str)
		return cls.from_dict(data)
	
	def to_openai_content(self) -> str:
		"""
		Convert to OpenAI-compatible format (dict with call_id and output).
		Removes show_user and type fields as OpenAI doesn't support them.
		
		Returns:
			FunctionCallOutput as a JSON formated string
		"""
		# return {
		# 	"type": "function_call_output",
		# 	"call_id": self.call_id,
		# 	"output": self.output
		# }
		return self.to_json()


def convert_to_openai_format(conversation_history: list) -> list:
	"""
	Convert conversation history to OpenAI-compatible format.
	
	This function converts content to JSON formatted string and puts it in the content key of
	the following dict:
	{
			"role": 
			"content": 
	}
	
	Args:
		conversation_history: List of message dicts with 'role' and 'content' keys.
			Content can be:
			- MessageContent instance
			- FunctionCallOutput instance
			- Dict with 'type' field
			- String (already in OpenAI format)
	
	Returns:
		List of message dicts in OpenAI-compatible format (role/content only, content is a JSON formatted string)
	"""
	openai_history = []
	
	for msg in conversation_history:
		role = msg.get("role")
		content = msg.get("content")
		
		# Handle different content types
		if isinstance(content, MessageContent):
			# MessageContent instance - convert to string
			openai_content = content.to_openai_content()
		elif isinstance(content, FunctionCallOutput):
			# FunctionCallOutput instance - convert to dict
			openai_content = content.to_openai_content()
		elif isinstance(content, dict):
			# Dictionary - check type and convert accordingly
			content_type = content.get("type")
			if content_type == "message":
				# Extract just the content string
				openai_content = content.get("content", "")
				openai_show_user = content.get("show_user", True)
			elif content_type == "function_call_output":
				# Extract call_id and output
				openai_content = json.dumps({
					"type": "function_call_output",
					"call_id": content.get("call_id", ""),
					"output": content.get("output", ""),
					"show_user": content.get("show_user", False)
				})
			else:
				# Unknown type, try to use as-is (might already be OpenAI format)
				openai_content = content
		elif isinstance(content, str):
			# Already a string, use as-is
			openai_content = content
		else:
			# Unknown type, log warning and skip
			import logging
			logger = logging.getLogger(__name__)
			logger.warning(f"Unknown content type in conversation history: {type(content)}")
			continue
		
		openai_history.append({
			"role": role,
			"content": openai_content
		})
	
	return openai_history
