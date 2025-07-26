from app.routes.api import api_bp
from app.routes.auth import auth_bp
from app.routes.bland import bland_bp
from app.routes.dashboard import dashboard_bp
from app.routes.twilio_phone import twilio_bp
from app.routes.twilio_sms import sms_bp
from app.routes.web import web_bp


def init_app(app):
	app.register_blueprint(auth_bp)
	app.register_blueprint(web_bp)
	app.register_blueprint(api_bp, url_prefix="/api")
	app.register_blueprint(bland_bp)
	app.register_blueprint(twilio_bp)
	app.register_blueprint(sms_bp)
	app.register_blueprint(dashboard_bp)
