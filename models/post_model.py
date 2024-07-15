from sqlalchemy import TEXT, VARCHAR, Column
from models.base_model import Base


class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(TEXT, primary_key=True)
    image_url = Column(TEXT)
    caption = Column(VARCHAR(255))