from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from .database import Base
from datetime import datetime

class SavedItem(Base):
    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(String) # e.g., "brand", "logo", "content", "colors"
    content = Column(JSON) # Store flexible data
    created_at = Column(DateTime, default=datetime.utcnow)
