import logging
import sqlite3

from flask import Blueprint, jsonify, request

from app.agent import Agent
from app.routes.auth import login_required

api_bp = Blueprint("api", __name__)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

agent = Agent()


@api_bp.route("/chat", methods=["POST"])
@login_required
def chat():
	try:
		data = request.get_json()
		user_message = data.get("message", "")
		session_id = data.get("session_id")

		if not user_message:
			logger.error("No message provided in request")
			return jsonify({"error": "No message provided"}), 400

		logger.info(f"=== Processing message with session ID: {session_id} ===")
		logger.debug(f"Input message: {user_message}")

		try:
			response = agent.process_message(user_message, session_id)
			logger.info("Successfully processed message")
			return jsonify({"response": response})

		except ValueError as ve:
			logger.error(f"Validation error: {ve!s}", exc_info=True)
			return jsonify({"error": str(ve)}), 400

		except sqlite3.Error as dbe:
			logger.error(f"Database error: {dbe!s}", exc_info=True)
			return jsonify({"error": "Database error occurred. Please try again."}), 500

		except Exception as e:
			logger.error(f"Error processing message: {e!s}", exc_info=True)
			return jsonify(
				{"error": "An unexpected error occurred. Please try again."},
			), 500
	except Exception as e:
		logger.error(f"Unexpected error in chat route: {e!s}", exc_info=True)
		return jsonify(
			{"error": "An unexpected error occurred. Please try again."},
		), 500


@api_bp.route("/clear-data", methods=["POST"])
@login_required
def clear_data():
	try:
		data = request.get_json()
		session_id = data.get("session_id")

		logger.info(f"=== Clearing data for session ID: {session_id} ===")
		agent.clear_memory(session_id)
		logger.info("Successfully cleared memory")
		return jsonify({"message": "Chat state reset successfully"}), 200

	except Exception as e:
		logger.error(f"Error clearing memory: {e!s}", exc_info=True)
		return jsonify(
			{"error": "An error occurred while clearing memory. Please try again."},
		), 500
