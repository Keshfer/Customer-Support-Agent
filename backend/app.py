from flask import Flask, jsonify
from flask_cors import CORS
from backend import config
import logging
from backend.routes.web_crawl import crawl_bp

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Flask app
app.config['DEBUG'] = config.FLASK_DEBUG
app.config['ENV'] = config.FLASK_ENV

# Enable CORS for all routes
CORS(app)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running."""
    return jsonify({"status": "healthy"}), 200

# Register blueprints for route modules
# Blueprints allow us to organize routes into separate modules
try:
	# Import and register website scraping routes
	app.register_blueprint(crawl_bp, url_prefix='/api')
	logger.info("Registered web_crawl blueprint")
except ImportError as e:
	# Log warning if blueprint can't be imported (e.g., during initial setup)
	logger = logging.getLogger(__name__)
	logger.warning(f"Could not import web_crawl blueprint: {e}")

# Import and register chat routes
try:
	from backend.routes.chat import chat_bp
	app.register_blueprint(chat_bp, url_prefix='/api')
	logger.info("Registered chat blueprint")
except ImportError as e:
	# Log warning if blueprint can't be imported (e.g., during initial setup)
	logger.warning(f"Could not import chat blueprint: {e}")

# Import and register conversation history routes
try:
	from backend.routes.conversation_history import conversation_history_bp
	app.register_blueprint(conversation_history_bp, url_prefix='/api')
	logger.info("Registered conversation history blueprint")
except ImportError as e:
	# Log warning if blueprint can't be imported (e.g., during initial setup)
	logger.warning(f"Could not import conversation history blueprint: {e}")

if __name__ == '__main__':
    # Validate configuration before starting
    try:
        config.validate_config()
        app.run(host='0.0.0.0', port=5000, debug=config.FLASK_DEBUG)
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please ensure all required environment variables are set in .env file")