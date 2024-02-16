from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

# USER
class User(BaseModel):
    id:Optional[int] = None
    email:str = Field(default="email@email.com", min_length=8, max_length=50)
    password:str = Field( min_length=4, max_length=150)
    admin:Optional[bool]
    date_joined:datetime
    
    class config:
        orm_mode = True
        
class UserUpdate(BaseModel):
    email:Optional[str] = Field(default=None, min_length=8, max_length=50)
    password:Optional[str] = Field(default=None, min_length=8, max_length=50)
    admin:Optional[bool]
    
    class config:
        orm_mode = True    
        
class Response(BaseModel):
    message:str
    
#LOGIN
class Login(BaseModel):
    
    email:str 
    password:str
   
    class config:
        orm_mode = True

    
class Course(BaseModel):
    id:Optional[int] = None 
    nombre:str = Field(min_length=4 ,max_length=50)
    
    
#ESTUDIANTES
class Studend(BaseModel):
    id:Optional[int] = None
    email:str = Field(default="email@email.com", min_length=8, max_length=50)
    password:str = Field( min_length=4, max_length=150)
    date_joined:datetime
    program:int
    birth_date:Optional[date] = None
    document_number:str = Field( min_length=4, max_length=50)
    first_name:str = Field( min_length=4, max_length=50)
    middle_name:str = Field( min_length=4, max_length=50)
    last_name:str= Field( min_length=4, max_length=50)
    
    class config:
        orm_mode = True    
    
    
class StudendResponse(BaseModel):
    id:Optional[int] = None
    program:int
    birth_date:Optional[date] = None
    document_number:str 
    first_name:str 
    middle_name:str
    last_name:str
      
    
class StudendUpdated(BaseModel):
    email:str = Field(default="email@email.com", min_length=8, max_length=50)
    password:str = Field( min_length=4, max_length=150)
    program:int
    birth_date:Optional[date] = None
    document_number:str = Field( min_length=4, max_length=50)
    first_name:str = Field( min_length=4, max_length=50)
    middle_name:str = Field( min_length=4, max_length=50)
    last_name:str= Field( min_length=4, max_length=50)
    
    class config:
        orm_mode = True    

class Enrollments(BaseModel):
    score:float = Field(default=0, ge=0, le=5)

    
    
class SubjectBase(BaseModel):
    id:Optional[int] = None
    name: str

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: int

    class Config:
        orm_mode = True

class PrerequisiteBase(BaseModel):
    subject_id: int
    prerequisite_id: int

class PrerequisiteCreate(PrerequisiteBase):
    pass

class Prerequisite(PrerequisiteBase):
    pass

class ProgramBase(BaseModel):
    id:Optional[int] = None
    name: str
    code: str
    description: str

class ProgramCreate(ProgramBase):
    pass

class Program(ProgramBase):
    id: int

    class Config:
        orm_mode = True

class StudentBase(BaseModel):
    type_document: str
    document_number: str
    birth_date: date
    program: int
    user: int

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int

    class Config:
        orm_mode = True

class EnrollmentBase(BaseModel):
    student_id: int
    subject_id: int
    score: int
    state: str

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    id: int

    class Config:
        orm_mode = True