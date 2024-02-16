from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from utils.autentication import hash_password, check_password, generate_access_token
from database.db import get_db
from sqlalchemy.orm import Session 
from router.user_router import permission_admin, get_token
from models.model import User, Student, Program
from schema.schema import (User as user_schema, UserUpdate as user_update_schema, 
                           Response, Login as login_schema, Studend as student_schema, ProgramBase as program_schema)
from typing import List
from middleware.verify_token_route import VerifyTokenRoute


router = APIRouter(route_class=VerifyTokenRoute,
                    prefix="/program",
                    tags=["Programs"]
)


@router.get('/list/', response_model=List[program_schema])
def program_list(db:Session = Depends(get_db)):
    program = db.query(Program).all()
    if not program:
        raise HTTPException(status_code=404, detail="No existen programas")
    return program


@router.get('/{id}/', response_model=program_schema)
def get_program(id:int, db:Session = Depends(get_db)):
    program = db.query(Program).filter_by(id=id).first()
    if not program:
        raise HTTPException(status_code=404, detail="El Programa no existe")
    else:
        return program
    

@router.post('/', response_model=program_schema)
def post_program(entrada:program_schema, token: str = Depends(get_token), db:Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    program = db.query(Program).filter_by(code=entrada.code).first()
    if program:
        raise HTTPException(status_code=409, detail="Ya existe un programa con este código")
    
    program = Program(name=entrada.name, code=entrada.code, description=entrada.description)
    
    db.add(program)
    db.commit()
    db.refresh(program)
    
    return program


@router.put('/{id}/', response_model=program_schema)
def put_program(id:int, entrada:program_schema, token: str = Depends(get_token), db:Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    program = db.query(Program).filter_by(id=id).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="El programa no existe")
    
    program.name=entrada.name if entrada.name else program.name
    program.code=entrada.code if entrada.code else program.code
    program.description=entrada.description if entrada.description else program.description
    db.commit()
    db.refresh(program)
    return program


@router.delete('/{id}/', response_model=Response)
def deleted_program(id:int, token: str = Depends(get_token), db:Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    program = db.query(Program).filter_by(id=id).first()
    if not program:
        raise HTTPException(status_code=404, detail="El programa no existe")
    db.delete(program)
    db.commit()
    return JSONResponse(content=None, status_code=204)
    