from database.db import Base
from sqlalchemy import Column, Integer, Boolean, DateTime, String, Date, ForeignKey, Text, Float
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(length=50), unique=True)
    password = Column(String(length=150))
    admin = Column(Boolean)
    date_joined = Column(DateTime)
    


class Program(Base):
    __tablename__ = 'program'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=50))
    code = Column(String(length=50), unique=True)
    description = Column(Text, nullable=True)
    
    
class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(length=50), nullable=False)
    middle_name =  Column(String(length=50))
    last_name = Column(String(length=50), nullable=False)
    document_number = Column(String(length=50))
    birth_date = Column(Date)
    program = Column(Integer, ForeignKey("program.id", ondelete="CASCADE"), nullable=False)
    user = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    enrollments = relationship("Enrollment", back_populates="student")

class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=50))
    
    enrollments = relationship("Enrollment", back_populates="subject")

    
class Prerequisite(Base):
    __tablename__ = 'prerequisites'

    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete="CASCADE"), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey('subjects.id', ondelete="CASCADE"), primary_key=True)


class Enrollment(Base):
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete="CASCADE"))
    score = Column(Float, nullable=True, default=0.0)
    approved = Column(Boolean, default=False)
    
    student = relationship("Student", back_populates="enrollments")
    subject = relationship("Subject", back_populates="enrollments")