from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.utilities.database import AdminDatabaseManager

auth_bp = Blueprint("auth", __name__)
admin_db_manager = AdminDatabaseManager()


def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if "user_id" not in session:
			return redirect(url_for("auth.login"))
		return f(*args, **kwargs)

	return decorated_function


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email")
		password = request.form.get("password")
		remember = request.form.get("remember-me") == "on"

		# Admin authentication
		admin = admin_db_manager.get_admin_by_email(email)
		if admin and admin.check_password(password):
			session["user_id"] = admin.id
			session["user_email"] = admin.email
			session["user_name"] = admin.name
			session["user_role"] = "admin"

			if remember:
				session.permanent = True

			# Update last login timestamp
			admin_db_manager.update_last_login(admin.id)

			return redirect(url_for("main.index"))
		else:
			flash("Invalid email or password", "error")

	return render_template("login.html")


@auth_bp.route("/logout")
def logout():
	session.clear()
	return redirect(url_for("auth.login"))
