from flask import Flask, jsonify
from flask_cors import CORS
import config

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

# TODO: Register blueprints here when routes are created
# from routes.chat import chat_bp
# from routes.web_crawl import web_crawl_bp
# app.register_blueprint(chat_bp, url_prefix='/api')
# app.register_blueprint(web_crawl_bp, url_prefix='/api')

if __name__ == '__main__':
    # Validate configuration before starting
    try:
        config.validate_config()
        app.run(host='0.0.0.0', port=5000, debug=config.FLASK_DEBUG)
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please ensure all required environment variables are set in .env file")