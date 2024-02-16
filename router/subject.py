from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from utils.autentication import hash_password, check_password, generate_access_token
from database.db import get_db
from sqlalchemy.orm import Session
from router.user_router import permission_admin, get_token
from models.model import User, Student, Subject, Prerequisite
from schema.schema import (User as user_schema, UserUpdate as user_update_schema, 
                           Response, Login as login_schema, Studend as student_schema, SubjectBase as subject_schema)
from middleware.verify_token_route import VerifyTokenRoute

from typing import List

router = APIRouter( route_class=VerifyTokenRoute,
                    prefix="/subject",
                    tags=["Subject"]
)

@router.get('/list/', response_model=List[subject_schema])
def subject_list(db:Session = Depends(get_db)):
    subject = db.query(Subject).all()
    if not subject:
        raise HTTPException(status_code=404, detail="No existen Materias")
    return subject


@router.get('/{id}/', response_model=subject_schema)
def get_subject(id:int, db:Session = Depends(get_db)):
    subject = db.query(Subject).filter_by(id=id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="La materia no existe")
    else:
        return subject
    

@router.post('/', response_model=subject_schema)
def post_subject(entrada:subject_schema, token: str = Depends(get_token), db:Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    subject = db.query(Subject).filter_by(name=entrada.name).first()
    if subject:
        raise HTTPException(status_code=409, detail="Ya existe una materia con este nombre")
    
    subject = Subject(name=entrada.name)
    
    db.add(subject)
    db.commit()
    db.refresh(subject)
    
    return subject


@router.put('/{id}/', response_model=subject_schema)
def put_subject(id:int, entrada:subject_schema, token: str = Depends(get_token), db:Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    subject = db.query(Subject).filter_by(id=id).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="La materia no existe")
    
    subject.name=entrada.name if entrada.name else subject.name
   
    db.commit()
    db.refresh(subject)
    return subject


@router.delete('/{id}/', response_model=Response)
def deleted_subject(id:int, token: str = Depends(get_token), db:Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    subject = db.query(Subject).filter_by(id=id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="La materia no existe")
    db.delete(subject)
    db.commit()
    return JSONResponse(content=None, status_code=204)
    
    
@router.post("/assign_prerequisites/{subject_id}")
def assign_prerequisites(subject_id: int, requisites: list[int], token: str = Depends(get_token), db: Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    subject_master = db.query(Subject).filter_by(id=subject_id).first()
    if not subject_master:
        raise HTTPException(status_code=404, detail="La matería no existe")

    for requisite_id in requisites:
        requisite = db.query(Subject).filter_by(id=requisite_id).first()
        if requisite is None:
            raise HTTPException(status_code=404, detail="La materia "+ str(requisite_id)+ " no existe")

    for requisite_id in requisites:
        existing_prerequisite = db.query(Prerequisite).filter_by(subject_id=subject_id, prerequisite_id=requisite_id).first()
        if not existing_prerequisite: 
            subject = Prerequisite(subject_id=subject_id, prerequisite_id=requisite_id)
        
            db.add(subject)
            db.commit()
            db.refresh(subject)
        
    content = 'Asignación de requisitos para la materia '+subject_master.name+' establecido correctamente'
    return JSONResponse(content=content, status_code=200)