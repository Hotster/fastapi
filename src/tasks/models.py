from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, UUID, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

from database import Base


class Task(Base):
    __tablename__ = 'task'

    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(length=255), nullable=False)
    description = Column(String(length=1000))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)
    due_date = Column(TIMESTAMP(timezone=True))
    done_at = Column(TIMESTAMP(timezone=True))
    owner_id = Column(UUID, ForeignKey('app_user.id'), nullable=False)
    owner = relationship('User', back_populates='tasks')
