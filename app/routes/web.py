from flask import Blueprint, redirect, render_template, url_for

from app.routes.auth import login_required

web_bp = Blueprint("main", __name__)


@web_bp.route("/")
@login_required
def index():
	return redirect(url_for("main.chat_page"))


@web_bp.route("/chat")
@login_required
def chat_page():
	return render_template("index.html")
