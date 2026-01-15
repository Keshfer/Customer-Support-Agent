from message import *
from website import *

try:
	messageObj = Message()

	messageObj.id = 123
	messageObj.conversation_id = "77777"
	messageObj.message = "yes that will do"

	print(messageObj.to_dict())
	print("✓ Message object created successfully!")

	websiteObj = Website()
	websiteObj.id = 456
	websiteObj.url = "https://www.google.com"
	websiteObj.title = "Google"
	websiteObj.scraped_at = datetime.now(timezone.utc)
	websiteObj.status = "completed"

	print(websiteObj.to_dict())
	print("✓ Website object created successfully!")
except Exception as e:
	print(f"Error: {e}")

