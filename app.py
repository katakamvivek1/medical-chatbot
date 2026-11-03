"""
Medical Chatbot - Flask entry point (Day 1).

Day 1 goal: a working web app with a chat page and a JSON API.
The "brain" (src/chat.py) is a simple placeholder today. On Day 3 we
replace it with RAG (LangChain + vector store + LLM) without touching
this file or the frontend - that separation is the point of today.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from src.chat import get_answer

# Read settings from a .env file (if present) into environment variables.
load_dotenv()

MAX_MESSAGE_LENGTH = 1000  # protect the app from huge inputs


def create_app() -> Flask:
    """Application factory: builds and returns the Flask app.

    Using a factory (instead of a global app) makes testing easier:
    each test can create a fresh app.
    """
    app = Flask(__name__)

    @app.get("/")
    def home():
        """Serve the chat page."""
        return render_template("index.html")

    @app.get("/health")
    def health():
        """Simple check used by Docker / hosting platforms (Day 4)."""
        return jsonify(status="ok")

    @app.post("/api/chat")
    def chat():
        """Receive a user message as JSON and return the bot's answer.

        Request body:  {"message": "What is diabetes?"}
        Response body: {"answer": "...", "sources": [...]}
        """
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()

        # Input validation: never trust what the browser sends.
        if not message:
            return jsonify(error="Message cannot be empty."), 400
        if len(message) > MAX_MESSAGE_LENGTH:
            return jsonify(
                error=f"Message is too long (max {MAX_MESSAGE_LENGTH} characters)."
            ), 400

        result = get_answer(message)
        return jsonify(result)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
