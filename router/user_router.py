from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Header
from datetime import datetime
from utils.autentication import hash_password, handle_authorization
from schema.schema import User
from database.db import get_db
from sqlalchemy.orm import Session 
from models.model import User
from schema.schema import User as user_schema, UserUpdate as user_update_schema, Response, Login as login_schema
from middleware.verify_token_route import VerifyTokenRoute
from typing import List

router = APIRouter(route_class=VerifyTokenRoute,
    prefix="/user",
    tags=["Users"]
)

def get_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Bearer token")
    return authorization.split("Bearer ")[1]


def permission_admin(token, db:Session = Depends(get_db)):
    decoded_token = handle_authorization(token, output=True)
    user_id = decoded_token.get('sub')
    user = db.query(User).filter_by(id=user_id).first()
    if user:
        if user.admin:
            return True
    return False


def return_user_id(token, db:Session = Depends(get_db)):
    decoded_token = handle_authorization(token, output=True)
    user_id = decoded_token.get('sub')
    if user_id:
        return user_id
    return False


@router.get('/list/', response_model=List[user_schema])
def user_list( db:Session = Depends(get_db)):
    user = db.query(User).all()
    if not user:
        raise HTTPException(status_code=404, detail="No existen usuarios")
    return user


@router.get('/{id}/', response_model=user_schema)
def get_user(id:int, db:Session = Depends(get_db)):
    user = db.query(User).filter_by(id=id).first()
    if not user:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    else:
        return user
    

@router.post('/', response_model=user_schema)
def post_user(entrada:user_schema, token: str = Depends(get_token), db:Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    password = hash_password(entrada.password)
    user = db.query(User).filter_by(email=entrada.email).first()
    if user:
        raise HTTPException(status_code=409, detail="Existe un usuario con el correo ingresado")
    
    user = User(email=entrada.email, password=password, admin=entrada.admin, date_joined=datetime.now())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put('/{id}/', response_model=user_schema)
def put_user(id:int, entrada:user_update_schema, token: str = Depends(get_token), db:Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    user = db.query(User).filter_by(id=id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    
    user.email = entrada.email if entrada.email else user.email
    user.password = entrada.password if entrada.password else user.password
    user.admin = entrada.admin if entrada.admin else user.admin
    db.commit()
    db.refresh(user)
    return user


@router.delete('/{id}/', response_model=Response)
def deleted_user(id:int, token: str = Depends(get_token), db:Session = Depends(get_db)):
    admin_permission = permission_admin(token, db)
    if not admin_permission:
        raise HTTPException(status_code=401, detail="No tienes permiso de administrador")
    
    user = db.query(User).filter_by(id=id).first()
    if not user:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    db.delete(user)
    db.commit()
    return JSONResponse(content=None, status_code=204)
    
