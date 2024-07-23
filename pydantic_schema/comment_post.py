from pydantic import BaseModel
from typing import Optional

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: str

class CommentResponse(CommentBase):
    id: str
    post_id: str
    user_id: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True
