from sqlalchemy import TEXT, VARCHAR, Column, ForeignKey
from sqlalchemy.orm import relationship
from models.base_model import Base

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(TEXT, primary_key=True)
    image_url = Column(TEXT)
    caption = Column(VARCHAR(255))
    user_id = Column(TEXT, ForeignKey("users.id"))
    
    user = relationship("UserModel", back_populates="posts")
    saved_posts = relationship("SavedModel", back_populates="post")
