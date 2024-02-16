from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from router.user_router import permission_admin, get_token
from utils.autentication import hash_password, check_password, generate_access_token
from schema.schema import User
from sqlalchemy.exc import IntegrityError
from database.db import get_db
from sqlalchemy.orm import Session
from models.model import User, Student, Enrollment, Subject, Prerequisite, Program
from schema.schema import (Response, Login as login_schema, Studend as student_schema,
                           StudendResponse as student_response, StudendUpdated as student_updated_schema, 
                           SubjectBase as subject_schema, Enrollments as enrollments_shema)
from typing import List
from middleware.verify_token_route import VerifyTokenRoute



router = APIRouter(route_class=VerifyTokenRoute,
    prefix="/student",
    tags=["Students"]
)

#ADMIN
@router.get('/list/', response_model=List[student_response])
def student_list(db:Session = Depends(get_db)):
    student = db.query(Student).all()
    if not student:
        raise HTTPException(status_code=404, detail="No existen estudiantes registrados.")
    return student


@router.get('/{student_id}/', response_model=student_response)
def get_student(student_id:int, db:Session=Depends(get_db)):
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")
    else:
        return student
    

@router.post('/', response_model=student_response)
def post_student(entrada: student_schema, token: str = Depends(get_token), db: Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")

    try:
        password = hash_password(entrada.password)

        user = db.query(User).filter_by(email=entrada.email).first()
        if user:
            raise HTTPException(status_code=409, detail="Existe un usuario con el correo ingresado")

        student = db.query(Student).filter_by(document_number=entrada.document_number).first()
        if student:
            raise HTTPException(status_code=409, detail="Existe un estudiante con el número de documento ingresado")

        program = db.query(Program).filter_by(id=entrada.program).first()
        if not program:
            raise HTTPException(status_code=409, detail="No existe el programa que intenta ingresar")

        user = User(email=entrada.email, password=password, date_joined=datetime.now())
        db.add(user)
        db.flush()

        student = Student(first_name=entrada.first_name, middle_name=entrada.middle_name,
                          last_name=entrada.last_name, document_number=entrada.document_number,
                          birth_date=entrada.birth_date, program=entrada.program, user=user.id
                          )
        db.add(student)
        db.commit()

        return student

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Violación de integridad en la base de datos")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
        
@router.put('/{student_id}/', response_model=student_response)
def put_student(student_id:int, entrada:student_updated_schema, token: str = Depends(get_token), db:Session=Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    existing_student = db.query(Student).filter(Student.document_number == entrada.document_number, Student.id != student_id).first()
    if existing_student:
        raise HTTPException(status_code=409, detail="Existe un estudiante con el número de documento ingresado")
    
    student = db.query(Student).filter_by(id=id).first()
    user = db.query(User).filter_by(id=student.user).first()

    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")
    
    existing_user = db.query(User).filter(User.email == entrada.email, User.id != user.id).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Existe un usuario con el correo ingresado")
    
    password = hash_password(entrada.password)
    
    student.program = entrada.program if entrada.program else student.program
    student.birth_date = entrada.birth_date if entrada.birth_date else student.birth_date
    student.document_number = entrada.document_number if entrada.document_number else student.document_number
    student.first_name = entrada.first_name if entrada.first_name else student.first_name
    student.middle_name = entrada.middle_name if entrada.middle_name else student.middle_name
    student.last_name = entrada.last_name if entrada.last_name else student.last_name
    user.email = entrada.email if entrada.email else user.email
    
    if entrada.password:
        password = hash_password(entrada.password)
        
    user.password=password
    db.commit()
    db.refresh(user)
    db.refresh(student)

    return student


@router.delete('/{student_id}/', response_model=Response)
def deleted_student(student_id:int, token: str = Depends(get_token), db:Session = Depends(get_db)):
    student = db.query(Student).filter_by(id=student_id).first()
    user = db.query(User).filter_by(id=student.user).first()
    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")
    db.delete(student)
    db.delete(user)
    db.commit()
    return JSONResponse(content=None, status_code=204)
    

@router.get('/{student_id}/subject/', response_model=List[subject_schema])
def get_subject_by_student(student_id:int, db:Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter_by(student_id=student_id)
    print("enrollments",enrollments)
    if not enrollments:
        raise HTTPException(status_code=404, detail="El estudiante no tiene inscrito materias")
    subjects = [db.query(Subject).filter_by(id=enrollment.subject_id).first() for enrollment in enrollments]
    
    return  subjects


@router.get('/{student_id}/failed_subjects/', response_model=List[subject_schema])
def get_failed_subjects(student_id:int, db:Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id, Enrollment.score < 3.0).all()
    if not enrollments:
        raise HTTPException(status_code=404, detail="El estudiante no tiene inscrito materias")
    subjects = [db.query(Subject).filter_by(id=enrollment.subject_id).first() for enrollment in enrollments]
    
    return  subjects 


@router.get('/{student_id}/approved_subjects/', response_model=List[subject_schema])
def get_approved_subjects(student_id:int, db:Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id, Enrollment.score >= 3.0).all()
    if not enrollments:
        raise HTTPException(status_code=404, detail="El estudiante no tiene inscrito materias")
    subjects = [db.query(Subject).filter_by(id=enrollment.subject_id).first() for enrollment in enrollments]
    
    return  subjects 


@router.get('/{student_id}/average_grade/', response_model=Response)
def get_average_grade(student_id:int, db:Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
    if not enrollments:
        raise HTTPException(status_code=404, detail="El estudiante no tiene inscrito materias")
    
    total_score = 0
    total_subjects = 0
    
    for enrollment in enrollments:
        if enrollment.score:
            total_score += enrollment.score
            total_subjects += 1
            
    average_grade = total_score / total_subjects
        
    return JSONResponse(content={"average_grade": average_grade}, status_code=200)
    
  
@router.post('/{student_id}/enroll_subject/', response_model=Response)
def post_enroll_subject(student_id:int, subjects: List[int], db:Session = Depends(get_db)):
    
    student = db.query(Student).filter_by(id=student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")
    
    for subject_id in subjects:
        prerequisites = db.query(Prerequisite).filter_by(subject_id=subject_id).all()
        if prerequisites:
            for prerequisite in prerequisites:
                prerequisite_subject_id = prerequisite.prerequisite_id
                enrollment = db.query(Enrollment).filter_by(student_id=student_id, subject_id=subject_id).first()
                if enrollment:
                     raise HTTPException(status_code=400, detail=f"El estudiante ya tiene inscrita la materia {subject_id}")
                enrollment = db.query(Enrollment).filter_by(student_id=student_id, subject_id=prerequisite_subject_id, approved=True).first()
                if not enrollment:
                    raise HTTPException(status_code=400, detail=f"El estudiante no ha aprobado todos los requisitos para inscribir la materia {subject_id}")
                
        new_enrollment = Enrollment(student_id=student_id, score=0.0, subject_id=subject_id, approved=False)
        db.add(new_enrollment)
        db.commit()
       
    return JSONResponse(content='Incripción exitosa', status_code=200)
    

@router.put('/{student_id}/finish subject/{subject_id}/', response_model=enrollments_shema)
def put_finish_subject(student_id:int, subject_id:int, entrada:enrollments_shema,  db:Session = Depends(get_db)):
    student = db.query(Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="El estudiante no existe")
    
    subject = db.query(Subject).filter_by(id=subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="La materia no existe")
    
    enrollment = db.query(Enrollment).filter_by(student_id=student_id, subject_id=subject_id).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="El estudiante no tiene la materia inscrita")
    
    enrollment.score = entrada.score if entrada.score and entrada.score > 0 else  enrollment.score
    enrollment.approved = True if entrada.score >= 3.0 else False
    
    db.commit()
    db.refresh(enrollment)
    
    return JSONResponse(content='Se agregó el puntaje ', status_code=200)