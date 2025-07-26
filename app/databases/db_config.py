from datetime import UTC, datetime

import bcrypt
from sqlalchemy import (
	Column,
	DateTime,
	Float,
	ForeignKey,
	Integer,
	String,
	Text,
	create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.utilities.time_utils import get_current_time

Base = declarative_base()
AdminBase = declarative_base()  # New base for admin database


class AdminUser(AdminBase):
	__tablename__ = "admin_users"

	id = Column(Integer, primary_key=True)
	email = Column(String(120), unique=True, nullable=False)
	password_hash = Column(String(128), nullable=False)
	name = Column(String(100), nullable=False)
	created_at = Column(DateTime, default=get_current_time)

	def set_password(self, password):
		"""Hash and set the admin's password."""
		salt = bcrypt.gensalt()
		self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode(
			"utf-8",
		)

	def check_password(self, password):
		"""Check if the provided password matches the stored hash."""
		return bcrypt.checkpw(
			password.encode("utf-8"),
			self.password_hash.encode("utf-8"),
		)


class Table1(Base):
	__tablename__ = "table1"

	id = Column(String, primary_key=True)
	col1 = Column(String)
	col2 = Column(Float)

	# Relationships
	table2 = relationship("Table2", back_populates="table1", uselist=False)


class Table2(Base):
	__tablename__ = "table2"

	id = Column(Integer, primary_key=True)
	table1_id = Column(String, ForeignKey("table1.id"))

	# Relationship
	table1 = relationship("Table1", back_populates="table2")


# Database setup function
def init_db(db_url="sqlite:///myusage.db?check_same_thread=False"):
	engine = create_engine(db_url)
	Base.metadata.create_all(engine)
	return engine
