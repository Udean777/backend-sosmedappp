from pydantic import BaseModel

class LikedPost(BaseModel):
    post_id: str
    
    class Config:
        orm_mode = True
