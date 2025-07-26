from gevent import monkey

monkey.patch_all()
from app import create_app
from app.config import config

app = create_app()

if __name__ == "__main__":
	if config.ENV == "development":
		app.run(host="0.0.0.0", port=8000, debug=config.DEBUG)
	else:
		app.run(debug=config.DEBUG)
