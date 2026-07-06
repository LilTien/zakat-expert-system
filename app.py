from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from api.routes import api_bp


def create_app():
    """Application factory for the Flask backend."""
    app = Flask(__name__)

    # Enable CORS for all routes (necessary for separated frontend/backend)
    CORS(app)

    # Swagger UI Configuration
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Zakat Selangor KBES API",
            "description": "API documentation for the Knowledge-Based Expert System (KBES) handling Zakat calculations and Asnaf screening.",
            "version": "1.0.0"
        }
    }
    # Initialize Swagger
    Swagger(app, template=swagger_template)

    # Register API blueprints
    app.register_blueprint(api_bp)

    @app.route('/', methods=['GET'])
    def health_check():
        """
        Health Check Endpoint
        ---
        tags:
          - System
        responses:
          200:
            description: Returns the status of the engine
        """
        return {"status": "Zakat Selangor KBES Engine is running on Vercel."}, 200

    return app

# --- VERCEL REQUIREMENT ---
# Vercel needs the 'app' instance exposed globally at the module level.
app = create_app()

if __name__ == '__main__':
    # This block is only used when running locally (python app.py)
    app.run(debug=True, port=5000)