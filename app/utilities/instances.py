from flask import current_app


def get_db_manager():
	return current_app.db_manager


def get_admin_db_manager():
	return current_app.admin_db_manager


def get_tts():
	return current_app.tts
