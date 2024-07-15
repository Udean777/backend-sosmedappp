import os
import uuid
import cloudinary.uploader
from dotenv import load_dotenv
import cloudinary
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from db import get_db
from middleware.auth_middleware import auth_middleware
from models.post_model import Post


load_dotenv()

router = APIRouter()

cloudinary.config( 
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key = os.getenv("CLOUDINARY_API_KEY"),  
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

@router.post("/upload", status_code=201)
def uploas_post(image_url: UploadFile = File(...),
                caption: str = Form(),
                 db: Session = Depends(get_db),
                auth_dict = Depends(auth_middleware)):
    post_id = str(uuid.uuid4())
    image_res = cloudinary.uploader.upload(image_url.file, resource_type="image", folder=f"posts/{post_id}")
    
    new_post = Post(
        id=post_id,
        image_url=image_res["url"],
        caption=caption,
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post