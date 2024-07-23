from sqlalchemy import TEXT, Column, DateTime, ForeignKey, func
from models.base_model import Base
from sqlalchemy.orm import relationship

class LikedModel(Base):
    __tablename__ = 'liked_posts'
    
    id = Column(TEXT, primary_key=True)
    post_id = Column(TEXT, ForeignKey("posts.id"))
    user_id = Column(TEXT, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    post = relationship("Post")
    user = relationship("UserModel", back_populates="liked_posts")
