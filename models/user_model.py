from sqlalchemy import TEXT, VARCHAR, Column, LargeBinary
from models.base_model import Base


class UserModel(Base):
    __tablename__ = 'users'
    
    id = Column(TEXT, primary_key=True)
    username = Column(VARCHAR(100))
    email = Column(VARCHAR(100))
    password = Column(LargeBinary)