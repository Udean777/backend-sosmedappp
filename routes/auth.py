import os
import uuid
import bcrypt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
import jwt
from sqlalchemy.orm import Session, joinedload
from db import get_db
from middleware.auth_middleware import auth_middleware
from models.user_model import UserModel
from pydantic_schema.user_create import UserCreate
from pydantic_schema.user_login import UserLogin

load_dotenv()
router = APIRouter()

@router.post("/signup", status_code=201)
def signup(user: UserCreate, db: Session=Depends(get_db)):
    # membuat variable untuk user dengan email yang sama
    user_db = db.query(UserModel).filter(UserModel.email == user.email).first()
    
    # Periksa jika user ada dengan email yang sama
    if user_db:
        raise HTTPException(status_code=400, detail="User with the same email already exists!")
    
    # Hashing password dengan bcrypt
    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt(16))
    
    # Ubah variable user_db menjadi data yang baru
    user_db = UserModel(id=str(uuid.uuid4()), username=user.username, email=user.email, password=hashed_pw)
    
    # add ke database
    db.add(user_db)
    # commit ke database
    db.commit()
    # refresh data user_db agar dapat di-return
    db.refresh(user_db)
    
    return user_db

@router.post("/signin", status_code=200)
def signin(user: UserLogin, db: Session=Depends(get_db)):
    # membuat variable untuk user dengan email yang sama
    user_db = db.query(UserModel).filter(UserModel.email == user.email).first()
    
    # Kembalikan error jika user dengan email yang di input tidak ada
    if not user_db:
        raise HTTPException(status_code=400, detail="User with this email does not exists!")
    
    # Variable untuk validasi password 
    is_match = bcrypt.checkpw(user.password.encode(), user_db.password)
    
    # Jika password tidak sama, tampilkan error "Password is incorrect!"
    if not is_match:
        raise HTTPException(status_code=400, detail="Password is incorrect!")
    
    # Buat token jwt untuk autentikasi login
    token = jwt.encode({"id": user_db.id}, os.getenv("PASSWORD_KEY"))
    
    # Kembalikan token jwt dan user untuk autentikasi login
    return {"token": token, "user": user_db}

@router.get("/me")
def current_user(db: Session=Depends(get_db), user_dict=Depends(auth_middleware)):
    # Cek jika user saat ini ter autentikasi atau tidak
    user = db.query(UserModel).filter(UserModel.id == user_dict["uid"]).options(
        joinedload(UserModel.saved_posts),
        joinedload(UserModel.liked_posts)).first()
    
    # jika tidak maka kembalikan "user not found!"
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    
    # Kembalikan user nya
    return user

@router.post("/signout", status_code=200)
def signout(user_dict=Depends(auth_middleware)):
    if not user_dict:
        raise HTTPException(status_code=401, detail="User not authenticated!")
    
    return {"message": "Successfully signed out"}