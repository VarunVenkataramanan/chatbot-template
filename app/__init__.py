import os

from flask import Flask, redirect, request
from flask_session import Session

from app.utilities.database import AdminDatabaseManager, DatabaseManager
from app.utilities.text_to_speech import TextToSpeech


def create_app():
	app = Flask(__name__, template_folder="../templates", static_folder="../static")

	# Ensure databases directory exists and is writable
	databases_dir = os.path.join(os.path.dirname(__file__), "databases")
	os.makedirs(databases_dir, exist_ok=True)
	if not os.access(databases_dir, os.W_OK):
		raise RuntimeError(f"Database directory {databases_dir} is not writable")

	# Configure the app (e.g., load config from config.py)
	app.config.from_object("app.config.Config")

	# Set preferred URL scheme to HTTPS
	app.config["PREFERRED_URL_SCHEME"] = "https"

	# Force HTTPS
	@app.before_request
	def before_request():
		if not request.is_secure and app.config.get("ENV") != "development":
			url = request.url.replace("http://", "https://", 1)
			return redirect(url, code=301)

	# Initialize Flask-Session
	Session(app)

	# Initialize shared instances)
	app.db_manager = DatabaseManager()
	app.admin_db_manager = AdminDatabaseManager()
	app.tts = TextToSpeech()

	# Register blueprints
	from app.routes import init_app

	init_app(app)

	return app
