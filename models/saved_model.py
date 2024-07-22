from sqlalchemy import TEXT, Column, ForeignKey
from models.base_model import Base
from sqlalchemy.orm import relationship

class SavedModel(Base):
    __tablename__ = 'saved_posts'
    
    id = Column(TEXT, primary_key=True)
    post_id = Column(TEXT, ForeignKey("posts.id"))
    user_id = Column(TEXT, ForeignKey("users.id"))
    
    post = relationship("Post")
    user = relationship("UserModel", back_populates="saved_posts")