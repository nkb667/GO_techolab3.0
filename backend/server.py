from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Import our models and services
from models import *
from auth import AuthHandler, get_current_user, EmailService, require_role
from database import connect_to_mongo, close_mongo_connection, get_database

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app
app = FastAPI(title="GO Learning Platform API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Global variables for dependencies
db = None
auth_handler = None
email_service = EmailService()

@app.on_event("startup")
async def startup_event():
    global db, auth_handler
    await connect_to_mongo()
    db = await get_database()
    auth_handler = AuthHandler(db)

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Dependency to get database
async def get_db():
    return db

# Dependency to get current user with database injection
async def get_current_user_with_db(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database = Depends(get_db)
):
    auth_handler = AuthHandler(database)
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

# ============ AUTHENTICATION ENDPOINTS ============

@api_router.post("/auth/register", response_model=APIResponse)
async def register_user(user_data: UserCreate, database = Depends(get_db)):
    """Register a new user"""
    auth_handler = AuthHandler(database)
    
    # Check if user already exists
    existing_user = await auth_handler.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user_dict = user_data.dict()
    new_user = await auth_handler.create_user(user_dict)
    
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    # Send verification email
    verification_token = auth_handler.generate_verification_token(user_data.email)
    await email_service.send_verification_email(user_data.email, verification_token)
    
    return APIResponse(
        success=True,
        message="User registered successfully. Please check your email for verification.",
        data={"user_id": new_user.id}
    )

@api_router.post("/auth/login", response_model=Token)
async def login_user(credentials: dict, database = Depends(get_db)):
    """Login user"""
    auth_handler = AuthHandler(database)
    
    email = credentials.get('email')
    password = credentials.get('password')
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    user = await auth_handler.authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please check your email."
        )
    
    # Create access token
    access_token = auth_handler.create_access_token(
        data={"sub": user.id, "email": user.email, "role": user.role}
    )
    
    return Token(access_token=access_token, user=user)

@api_router.get("/auth/verify-email")
async def verify_email(token: str, database = Depends(get_db)):
    """Verify user email"""
    auth_handler = AuthHandler(database)
    
    email = await auth_handler.verify_email_token(token)
    success = await auth_handler.verify_user_email(email)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification failed"
        )
    
    return APIResponse(
        success=True,
        message="Email verified successfully"
    )

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user_with_db)):
    """Get current user information"""
    return current_user

# ============ USER MANAGEMENT ENDPOINTS ============

@api_router.get("/users", response_model=List[User])
async def get_users(
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Get all users (admin/teacher only)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    users = await database.users.find().to_list(1000)
    return [User(**user) for user in users]

@api_router.get("/users/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Get user by ID"""
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user = await database.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**user)

# ============ CLASS MANAGEMENT ENDPOINTS ============

@api_router.post("/classes", response_model=Class)
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Create a new class (teachers and admins only)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can create classes"
        )
    
    class_dict = class_data.dict()
    class_dict["teacher_id"] = current_user.id
    
    new_class = Class(**class_dict)
    await database.classes.insert_one(new_class.dict())
    
    return new_class

@api_router.get("/classes", response_model=List[Class])
async def get_classes(
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Get classes for current user"""
    if current_user.role == UserRole.TEACHER:
        classes = await database.classes.find({"teacher_id": current_user.id}).to_list(100)
    elif current_user.role == UserRole.ADMIN:
        classes = await database.classes.find().to_list(100)
    else:  # Student
        classes = await database.classes.find({"students": current_user.id}).to_list(100)
    
    return [Class(**cls) for cls in classes]

@api_router.post("/classes/{class_id}/join")
async def join_class(
    class_id: str,
    class_code: str,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Join a class using class code"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can join classes"
        )
    
    # Find class by code and ID
    class_doc = await database.classes.find_one({"id": class_id, "class_code": class_code})
    if not class_doc:
        raise HTTPException(status_code=404, detail="Invalid class code")
    
    # Check if student already in class
    if current_user.id in class_doc.get("students", []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this class"
        )
    
    # Add student to class
    await database.classes.update_one(
        {"id": class_id},
        {"$push": {"students": current_user.id}}
    )
    
    return APIResponse(
        success=True,
        message="Successfully joined class"
    )

# ============ LESSON ENDPOINTS ============

@api_router.post("/lessons", response_model=Lesson)
async def create_lesson(
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Create a new lesson (teachers and admins only)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can create lessons"
        )
    
    lesson_dict = lesson_data.dict()
    lesson_dict["created_by"] = current_user.id
    
    new_lesson = Lesson(**lesson_dict)
    await database.lessons.insert_one(new_lesson.dict())
    
    return new_lesson

@api_router.get("/lessons", response_model=List[Lesson])
async def get_lessons(
    difficulty: Optional[DifficultyLevel] = None,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Get all published lessons"""
    filter_query = {"is_published": True}
    if difficulty:
        filter_query["difficulty"] = difficulty
    
    lessons = await database.lessons.find(filter_query).sort("order_index", 1).to_list(100)
    return [Lesson(**lesson) for lesson in lessons]

@api_router.get("/lessons/{lesson_id}", response_model=Lesson)
async def get_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Get specific lesson"""
    lesson = await database.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if lesson is published or if user is creator/admin
    if not lesson["is_published"] and current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        if lesson["created_by"] != current_user.id:
            raise HTTPException(status_code=404, detail="Lesson not found")
    
    return Lesson(**lesson)

# ============ QUIZ ENDPOINTS ============

@api_router.post("/quizzes", response_model=Quiz)
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Create a new quiz"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers and admins can create quizzes"
        )
    
    quiz_dict = quiz_data.dict()
    quiz_dict["created_by"] = current_user.id
    quiz_dict["max_points"] = sum(q.points for q in quiz_data.questions)
    
    new_quiz = Quiz(**quiz_dict)
    await database.quizzes.insert_one(new_quiz.dict())
    
    return new_quiz

@api_router.get("/lessons/{lesson_id}/quizzes", response_model=List[Quiz])
async def get_lesson_quizzes(
    lesson_id: str,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Get quizzes for a specific lesson"""
    quizzes = await database.quizzes.find({"lesson_id": lesson_id, "is_active": True}).to_list(100)
    return [Quiz(**quiz) for quiz in quizzes]

@api_router.post("/quizzes/{quiz_id}/attempt", response_model=QuizAttempt)
async def start_quiz_attempt(
    quiz_id: str,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Start a new quiz attempt"""
    quiz = await database.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        max_score=quiz["max_points"]
    )
    
    await database.quiz_attempts.insert_one(attempt.dict())
    
    # Return quiz questions without correct answers
    quiz_for_student = Quiz(**quiz)
    for question in quiz_for_student.questions:
        question.correct_answer = ""  # Hide correct answer
    
    return attempt

# ============ PROGRESS ENDPOINTS ============

@api_router.post("/lessons/{lesson_id}/progress")
async def start_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Start or update lesson progress"""
    # Check if lesson exists
    lesson = await database.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Check if progress already exists
    existing_progress = await database.lesson_progress.find_one({
        "user_id": current_user.id,
        "lesson_id": lesson_id
    })
    
    if existing_progress:
        return APIResponse(success=True, message="Lesson already started")
    
    # Create new progress
    progress = LessonProgress(user_id=current_user.id, lesson_id=lesson_id)
    await database.lesson_progress.insert_one(progress.dict())
    
    return APIResponse(success=True, message="Lesson started")

@api_router.put("/lessons/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: str,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Mark lesson as completed"""
    lesson = await database.lessons.find_one({"id": lesson_id})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    # Update progress
    result = await database.lesson_progress.update_one(
        {"user_id": current_user.id, "lesson_id": lesson_id},
        {
            "$set": {
                "is_completed": True,
                "completed_at": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    if result.upserted_id or result.modified_count > 0:
        # Award points
        await database.users.update_one(
            {"id": current_user.id},
            {"$inc": {"points": lesson["points_reward"]}}
        )
        
        # Check for achievements
        await check_achievements(current_user.id, database)
    
    return APIResponse(success=True, message="Lesson completed")

# ============ ACHIEVEMENT SYSTEM ============

async def check_achievements(user_id: str, database):
    """Check and award achievements for a user"""
    # Get user stats
    lessons_completed = await database.lesson_progress.count_documents({
        "user_id": user_id,
        "is_completed": True
    })
    
    quizzes_completed = await database.quiz_attempts.count_documents({
        "user_id": user_id,
        "is_completed": True
    })
    
    # Get achievements user doesn't have yet
    user_achievements = await database.user_achievements.find({"user_id": user_id}).to_list(100)
    earned_achievement_ids = [ua["achievement_id"] for ua in user_achievements]
    
    available_achievements = await database.achievements.find({
        "is_active": True,
        "id": {"$nin": earned_achievement_ids}
    }).to_list(100)
    
    # Check each achievement
    for achievement in available_achievements:
        criteria = achievement["criteria"]
        earned = False
        
        if "lessons_completed" in criteria and lessons_completed >= criteria["lessons_completed"]:
            earned = True
        
        if earned:
            # Award achievement
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement["id"],
                progress=1.0
            )
            
            await database.user_achievements.insert_one(user_achievement.dict())
            
            # Award points
            await database.users.update_one(
                {"id": user_id},
                {"$inc": {"points": achievement["points_reward"]}}
            )

@api_router.get("/users/{user_id}/achievements", response_model=List[UserAchievement])
async def get_user_achievements(
    user_id: str,
    current_user: User = Depends(get_current_user_with_db),
    database = Depends(get_db)
):
    """Get user achievements"""
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    achievements = await database.user_achievements.find({"user_id": user_id}).to_list(100)
    return [UserAchievement(**achievement) for achievement in achievements]

# ============ BASIC ENDPOINTS ============

@api_router.get("/")
async def root():
    return {"message": "GO Learning Platform API"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)