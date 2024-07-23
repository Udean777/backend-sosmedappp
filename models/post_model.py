from sqlalchemy import TEXT, VARCHAR, Column, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.base_model import Base

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(TEXT, primary_key=True)
    image_url = Column(TEXT)
    caption = Column(VARCHAR(255))
    user_id = Column(TEXT, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("UserModel", back_populates="posts")
    saved_posts = relationship("SavedModel", back_populates="post")
