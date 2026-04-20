from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db, init_db
import models
from models import Course, Lesson, Quiz
from ai_service import AIService
import uvicorn
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="AI LMS Backend API")

# Initialize DB on startup
@app.on_event("startup")
def startup():
    init_db()

import hashlib
import os

def get_password_hash(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password, hashed_password):
    return get_password_hash(plain_password) == hashed_password

from pydantic import EmailStr

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class GenerateRequest(BaseModel):
    topic: str
    provider: str = "gemini"

@app.post("/register/")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    return {"status": "success", "message": "User registered successfully"}

@app.post("/login/")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {"status": "success", "username": db_user.username, "user_id": db_user.id}

@app.post("/generate-course/")
def generate_course(req: GenerateRequest, user_id: int, db: Session = Depends(get_db)):
    ai = AIService(provider=req.provider)
    curriculum = ai.generate_course_curriculum(req.topic)
    
    new_course = models.Course(title=req.topic, description=f"An AI-generated course on {req.topic}", instructor_id=user_id)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    for item in curriculum:
        lesson = models.Lesson(
            course_id=new_course.id,
            title=item.get('title'),
            content=ai.generate_lesson_content(req.topic, item.get('title')),
            order=item.get('order')
        )
        db.add(lesson)
    
    db.commit()
    return {"status": "success", "course_id": new_course.id, "lessons_count": len(curriculum)}

@app.get("/courses/", response_model=List[dict])
def get_courses(db: Session = Depends(get_db)):
    courses = db.query(Course).all()
    return [{"id": c.id, "title": c.title} for c in courses]

@app.get("/course/{course_id}")
def get_course_details(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    lessons = db.query(Lesson).filter(Lesson.course_id == course_id).order_by(Lesson.order).all()
    return {
        "course": {"id": course.id, "title": course.title, "description": course.description},
        "lessons": [{"id": l.id, "title": l.title, "content": l.content, "order": l.order} for l in lessons]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
