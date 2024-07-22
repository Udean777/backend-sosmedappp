from pydantic import BaseModel


class SavedPost(BaseModel):
    post_id: str