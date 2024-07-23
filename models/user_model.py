from sqlalchemy import TEXT, VARCHAR, Column, LargeBinary
from models.base_model import Base
from sqlalchemy.orm import relationship


class UserModel(Base):
    __tablename__ = 'users'
    
    id = Column(TEXT, primary_key=True)
    username = Column(VARCHAR(100))
    email = Column(VARCHAR(100))
    password = Column(LargeBinary)
    
    posts = relationship("Post", back_populates="user")
    saved_posts = relationship("SavedModel", back_populates="user")
    liked_posts = relationship("LikedModel", back_populates="user")
    comments = relationship("CommentModel", back_populates="user", cascade="all, delete-orphan")
