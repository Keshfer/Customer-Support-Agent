from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .base import Base

class Website(Base):
    """SQLAlchemy model for websites table."""
    __tablename__ = 'websites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), unique=True, nullable=False)
    title = Column(String(512))
    scraped_at = Column(DateTime, default=datetime.now(datetime.timezone.utc))
    status = Column(String(50))  # 'pending', 'completed', 'failed'
    
    def __repr__(self):
        return f"<Website(id={self.id}, url='{self.url}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'status': self.status
        }
