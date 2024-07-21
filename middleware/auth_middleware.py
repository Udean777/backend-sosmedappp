import os
from dotenv import load_dotenv
from fastapi import HTTPException, Header
import jwt

load_dotenv()

def auth_middleware(x_auth_token=Header()):
    try:
        # Periksa jika token tidak ada
        if not x_auth_token:
            raise HTTPException(status_code=401, detail="Authentication token is required")
        
        # Buat variable token yang di verifikasi
        verified_token = jwt.decode(x_auth_token, os.getenv("PASSWORD_KEY"), ["HS256"])
        
        # Periksa apakah token nya ter verifikasi
        if not verified_token:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        
        # Buat variable uid untuk menyimpan id yang sudah di samakan dengan token
        uid = verified_token.get("id")
        
        # Kembalikan uid dan token nya
        return {"uid": uid, "token": x_auth_token}
    
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")