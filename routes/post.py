import os
from typing import List
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
from models.comment_model import CommentModel
from models.liked_model import LikedModel
from models.post_model import Post
from models.saved_model import SavedModel
from models.user_model import UserModel
from pydantic_schema.comment_post import CommentCreate, CommentResponse
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
        user_id = auth_details["uid"]
        
        # Query posts with related data
        posts = db.query(Post).options(
            joinedload(Post.user),
            joinedload(Post.liked_posts).joinedload(LikedModel.user),
            joinedload(Post.saved_posts).joinedload(SavedModel.user),
            joinedload(Post.comments).joinedload(CommentModel.user)
        ).all()
        
        response = []
        for post in posts:
            liked_by_user = any(liked.user_id == user_id for liked in post.liked_posts)
            saved_by_user = any(saved.user_id == user_id for saved in post.saved_posts)
            
            comments = []
            for comment in post.comments:
                comments.append({
                    "id": comment.id,
                    "content": comment.content,
                    "created_at": comment.created_at,
                    "updated_at": comment.updated_at,
                    "user": {
                        "id": comment.user.id,
                        "username": comment.user.username,
                        "email": comment.user.email
                    }
                })
                
            response.append({
                "id": post.id,
                "image_url": post.image_url,
                "caption": post.caption,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "liked_by_user": liked_by_user,
                "saved_by_user": saved_by_user,
                "likes_count": len(post.liked_posts),
                "saves_count": len(post.saved_posts),
                "comments": comments,
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
    
@router.post("/liked")
def liked_post(post: SavedPost,
               db: Session=Depends(get_db),
               auth_details=Depends(auth_middleware)):
    user_id = auth_details["uid"]
    
    liked_post = db.query(LikedModel).filter(LikedModel.post_id == post.post_id, LikedModel.user_id == user_id).first()
    
    if liked_post:
        db.delete(liked_post)
        db.commit()
        return {"message": False}
    else:
        new_liked_post = LikedModel(id=str(uuid.uuid4()), post_id=post.post_id, user_id=user_id)
        db.add(new_liked_post)
        db.commit()
        return {"message": True}
    
@router.get("/list/liked")
def list_liked_post(db: Session = Depends(get_db),
                    auth_details = Depends(auth_middleware)):
    user_id = auth_details["uid"]
    
    liked_posts = db.query(LikedModel).filter(LikedModel.user_id == user_id).options(
        joinedload(LikedModel.post).joinedload(Post.user),
    ).all()
    
    response = []
    for liked_post in liked_posts:
        post = liked_post.post
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

@router.post("/comments")
def create_comment(comment: CommentCreate,
                   db: Session = Depends(get_db),
                   auth_details = Depends(auth_middleware)):
    user_id = auth_details["uid"]
    
    new_comment = CommentModel(
        id=str(uuid.uuid4()),
        post_id=comment.post_id,
        user_id=user_id,
        content=comment.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return new_comment

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def list_comments(post_id: str, db: Session = Depends(get_db)):
    comments = db.query(CommentModel).filter(CommentModel.post_id == post_id).all()
    
    return comments

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: str, db: Session = Depends(get_db), auth_details = Depends(auth_middleware)):
    user_id = auth_details["uid"]
    comment = db.query(CommentModel).filter(CommentModel.id == comment_id, CommentModel.user_id == user_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or not authorized")
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}