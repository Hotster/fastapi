from datetime import datetime

from sqlalchemy import Column, UUID, String, TIMESTAMP

from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)
    username = Column(String(length=50), nullable=False)
    email = Column(String(length=250), nullable=False)
    password = Column(String(length=50), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
