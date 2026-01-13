from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .base import Base

class Message(Base):
    """SQLAlchemy model for messages/conversations table."""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(255), nullable=False, index=True)
    message = Column(Text, nullable=False)
    sender = Column(String(50), nullable=False)  # 'user' or 'agent'
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id='{self.conversation_id}', sender='{self.sender}')>"
    
    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'message': self.message,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
