import logging
import os
import re
from datetime import UTC, datetime, timedelta

from defusedxml import ElementTree
from sqlalchemy import create_engine, func
from sqlalchemy.orm import joinedload, sessionmaker

from app.models import (
	Account,
	AdminBase,
	AdminUser,
	Base,
	BillingInfo,
	Meter,
	Outage,
	Reading,
	Summary,
)
from app.utilities.time_utils import get_current_time


def setup_database_logging():
	"""Set up logging for database operations."""
	# Create output directory if it doesn't exist
	output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
	os.makedirs(output_dir, exist_ok=True)

	log_file = os.path.join(output_dir, "database.log")

	# Create logger
	logger = logging.getLogger("database")
	logger.setLevel(logging.DEBUG)
	logger.propagate = False  # Prevent logs from appearing in terminal

	# Remove existing handlers to avoid duplicates
	for handler in logger.handlers[:]:
		logger.removeHandler(handler)

	# Create file handler
	file_handler = logging.FileHandler(log_file)
	file_handler.setLevel(logging.DEBUG)

	# Create formatter
	formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
	file_handler.setFormatter(formatter)

	# Add handler to logger
	logger.addHandler(file_handler)

	return logger


# Initialize logger
db_logger = setup_database_logging()


class DatabaseManager:
	def __init__(
		self,
		db_url="sqlite:///app/databases/myusage.db",
	):
		self.engine = create_engine(db_url)
		Base.metadata.create_all(self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def get_customer_by_phone(self, phone_number):
		session = self.Session()
		try:
			account = session.query(Account).filter(Account.phone == phone_number).first()
			if account:
				# Refresh the account object to ensure it's fully loaded
				session.refresh(account)
			return account
		except Exception:
			return None
		finally:
			session.close()

	def get_billing_by_customer_id(self, account_id):
		session = self.Session()
		try:
			return session.query(BillingInfo).filter(BillingInfo.account_id == account_id).first()
		finally:
			session.close()


class AdminDatabaseManager:
	def __init__(
		self,
		db_url="sqlite:///app/databases/admin.db?check_same_thread=False",
	):
		self.engine = create_engine(db_url)
		AdminBase.metadata.create_all(self.engine)
		self.Session = sessionmaker(bind=self.engine)

	def create_admin(self, email, password, name):
		"""Create a new admin user with a hashed password."""
		session = self.Session()
		try:
			# Check if admin already exists
			existing_admin = session.query(AdminUser).filter(AdminUser.email == email).first()
			if existing_admin:
				return None

			admin = AdminUser(email=email, name=name)
			admin.set_password(password)
			session.add(admin)
			session.commit()
			session.refresh(admin)
			return admin
		finally:
			session.close()

	def get_admin_by_email(self, email):
		"""Get an admin by their email address."""
		session = self.Session()
		try:
			return session.query(AdminUser).filter(AdminUser.email == email).first()
		finally:
			session.close()

	def delete_admin(self, email):
		"""Delete an admin by their email address."""
		session = self.Session()
		try:
			admin = session.query(AdminUser).filter(AdminUser.email == email).first()
			if admin:
				session.delete(admin)
				session.commit()
				return True
			return False
		finally:
			session.close()

	def get_all_admins(self):
		"""Get all admin users from the database."""
		session = self.Session()
		try:
			return session.query(AdminUser).all()
		finally:
			session.close()
