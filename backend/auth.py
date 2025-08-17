import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
import os
from models import User, UserRole
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Security setup
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthHandler:
    def __init__(self, db):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def get_user_by_email(self, email: str):
        user = await self.db.users.find_one({"email": email})
        if user:
            return User(**user)
        return None
    
    async def get_user_by_id(self, user_id: str):
        user = await self.db.users.find_one({"id": user_id})
        if user:
            return User(**user)
        return None
    
    async def create_user(self, user_data: dict):
        # Hash password
        user_data["password"] = self.hash_password(user_data["password"])
        
        # Create user object to generate ID
        from models import User
        user_obj = User(**user_data)
        user_dict = user_obj.dict()
        
        # Create user in database
        result = await self.db.users.insert_one(user_dict)
        if result.inserted_id:
            return await self.get_user_by_id(user_obj.id)
        return None
    
    async def authenticate_user(self, email: str, password: str):
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        # Get password from database (since User model doesn't include password field)
        user_doc = await self.db.users.find_one({"email": email})
        if not user_doc or "password" not in user_doc:
            return None
            
        if not self.verify_password(password, user_doc["password"]):
            return None
        
        # Update last login
        await self.db.users.update_one(
            {"id": user.id},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return user
    
    def generate_verification_token(self, email: str) -> str:
        """Generate email verification token"""
        data = {"email": email, "purpose": "email_verification"}
        return self.create_access_token(data, timedelta(hours=24))
    
    async def verify_email_token(self, token: str) -> str:
        """Verify email verification token"""
        payload = self.decode_token(token)
        if payload.get("purpose") != "email_verification":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        return payload.get("email")
    
    async def verify_user_email(self, email: str):
        """Mark user email as verified"""
        result = await self.db.users.update_one(
            {"email": email},
            {"$set": {"is_verified": True}}
        )
        return result.modified_count > 0

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = None
):
    if db is None:
        # This will be injected in the main app
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database not configured"
        )
    
    auth_handler = AuthHandler(db)
    token = credentials.credentials
    payload = auth_handler.decode_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = await auth_handler.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

# Role-based access control decorators
def require_role(allowed_roles: list):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user or current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Email utility functions
class EmailService:
    def __init__(self):
        self.smtp_server = os.environ.get("SMTP_SERVER", "localhost")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")
        self.from_email = os.environ.get("FROM_EMAIL", "noreply@golearn.com")
    
    async def send_verification_email(self, email: str, token: str):
        """Send email verification"""
        verification_url = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token}"
        
        subject = "Verify your email - GO Learning Platform"
        body = f"""
        <html>
        <body>
            <h2>Welcome to GO Learning Platform!</h2>
            <p>Please click the link below to verify your email address:</p>
            <p><a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
            <p>If the button doesn't work, copy and paste this link into your browser:</p>
            <p>{verification_url}</p>
            <p>This link will expire in 24 hours.</p>
        </body>
        </html>
        """
        
        await self.send_email(email, subject, body)
    
    async def send_email(self, to_email: str, subject: str, body: str):
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # In production, you would use actual SMTP server
            # For now, we'll just log it
            print(f"EMAIL SENT TO: {to_email}")
            print(f"SUBJECT: {subject}")
            print(f"BODY: {body}")
            
        except Exception as e:
            print(f"Failed to send email: {e}")