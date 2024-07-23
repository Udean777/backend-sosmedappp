import os
import uuid
import cloudinary.uploader
from dotenv import load_dotenv
import cloudinary
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

from db import get_db
from middleware.auth_middleware import auth_middleware
from models.post_model import Post
from models.saved_model import SavedModel
from models.user_model import UserModel
from pydantic_schema.saved_post import SavedPost

load_dotenv()

router = APIRouter()

cloudinary.config( 
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key = os.getenv("CLOUDINARY_API_KEY"),  
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

@router.post("/upload", status_code=201)
def upload_post(image_url: UploadFile = File(...),
                caption: str = Form(),
                db: Session = Depends(get_db),
                auth_dict = Depends(auth_middleware)):
    try:
        logging.info("Start upload_post function")

        # Generate uuid for post
        post_id = str(uuid.uuid4())
        logging.info(f"Generated post_id: {post_id}")
        
        # Upload image to cloudinary and store in image_res
        logging.info("Uploading image to Cloudinary")
        image_res = cloudinary.uploader.upload(image_url.file, resource_type="image", folder=f"posts/{post_id}")
        logging.info(f"Image uploaded to Cloudinary: {image_res['url']}")
        
        # Create a new post
        new_post = Post(
            id=post_id,
            image_url=image_res["url"],
            caption=caption,
            user_id=auth_dict["uid"]
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        logging.info("New post committed to database")
        
        user = db.query(UserModel).filter(UserModel.id == auth_dict["uid"]).first()
        logging.info(f"User fetched from database: {user.id}")
        
        response = {
            "id": new_post.id,
            "image_url": new_post.image_url,
            "caption": new_post.caption,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
        
        logging.info("Returning response")
        return response
    except SQLAlchemyError as e:
        db.rollback()
        logging.error("Database error occurred", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logging.error("An error occurred", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
def list_post(db: Session = Depends(get_db),
              auth_details = Depends(auth_middleware)):
    try:
        posts = db.query(Post).options(joinedload(Post.user)).all()
        
        response = []
        for post in posts:
            response.append({
                "id": post.id,
                "image_url": post.image_url,
                "caption": post.caption,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "user": {
                    "id": post.user.id,
                    "username": post.user.username,
                    "email": post.user.email
                }
            })
        
        return response
    except SQLAlchemyError as e:
        logging.error("Database error occurred", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/saved")
def saved_post(post: SavedPost,
               db: Session=Depends(get_db),
               auth_details=Depends(auth_middleware)):
    
    user_id =  auth_details["uid"]
    
    saved_post = db.query(SavedModel).filter(SavedModel.post_id == post.post_id, SavedModel.user_id == user_id).first()
    
    if saved_post:
        db.delete(saved_post)
        db.commit()
        return {"message": False}
    else:
        new_saved_post = SavedModel(id=str(uuid.uuid4()), post_id=post.post_id, user_id=user_id)
        db.add(new_saved_post)
        db.commit()
        return {"message": True}
    
@router.get("/list/saved")
def list_saved_post(db: Session = Depends(get_db),
                    auth_details = Depends(auth_middleware)):
    user_id = auth_details["uid"]
    
    saved_posts = db.query(SavedModel).filter(SavedModel.user_id == user_id).options(
        joinedload(SavedModel.post).joinedload(Post.user),
    ).all()
    
    # Logging for debugging
    for saved_post in saved_posts:
        logging.info(f"Saved post: {saved_post.post}")
    
    response = []
    for saved_post in saved_posts:
        post = saved_post.post
        response.append({
            "id": post.id,
            "image_url": post.image_url,
            "caption": post.caption,
            "created_at": post.created_at,
                "updated_at": post.updated_at,
            "user": {
                "id": post.user.id,
                "username": post.user.username,
                "email": post.user.email
            }
        })
    
    return response
