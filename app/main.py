from fastapi import FastAPI
from database.db import Base, engine
from router.user_router import router as user_router
from router.student import router as student_router
from router.program import router as program_router
from router.subject import router as subject_router
from router.login import router as login_router


import uvicorn
from models import model

model.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(user_router)
app.include_router(student_router)
app.include_router(program_router)
app.include_router(subject_router)
app.include_router(login_router)


