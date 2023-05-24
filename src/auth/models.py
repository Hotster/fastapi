from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, UUID, String, TIMESTAMP

from database import Base


class User(Base):
    __tablename__ = 'app_user'

    id = Column(UUID, primary_key=True, default=uuid4)
    username = Column(String(length=50), nullable=False, unique=True)
    email = Column(String(length=250), nullable=False, unique=True)
    password = Column(String(length=50), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
