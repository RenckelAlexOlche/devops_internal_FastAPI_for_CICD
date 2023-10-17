import bcrypt
from fastapi import Depends, FastAPI, HTTPException, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app import crud, schemas
from app.utils import get_current_user
from app.crud import SECRET_KEY
from app.database import get_db
from app.services import UserService, TaskService

app = FastAPI(docs_url='/api/docs')
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")



@app.get('/')
def home_page(request: Request, db: get_db = Depends()):

    username = ''
    tasks = []

    logined = request.session.get('token') is not None

    if logined:
        user = get_current_user(db, request.session['token'])
        username = crud.get_user_by_id(db, user.id).username
        tasks = user.tasks

    return templates.TemplateResponse("home/home.html", {"request": request, "is_login_in": logined, "username": username, "tasks": tasks}) 



@app.get('/user/sign-in')
def sign_in_user_page(request: Request):
    return templates.TemplateResponse("user/sign-in/sign-in.html", {"request": request, "url_tab": "sign-in", "result": {}}) 



@app.post('/user/sign-in')
def sign_in_user_request(request: Request, user_login: schemas.UserLogin = Depends(schemas.UserLogin.as_form), db: get_db = Depends()):

    try:
        token = UserService.login(db, user_login)
        request.session['token'] = token
    except HTTPException as ex:
        result = ex.detail
        return templates.TemplateResponse("user/sign-in/sign-in.html", {"request": request, "url_tab": "sign-in", "result": result}) 

    return RedirectResponse(url="/", status_code=303)



@app.post('/user/sign-out')
def sign_out(request: Request):

    request.session.pop('token')
 
    return RedirectResponse(url="/", status_code=303)


@app.get('/user/sign-up')
def sign_up_user_page(request: Request):

    return templates.TemplateResponse("user/sign-up/sign-up.html", {"request": request, "url_tab": "sign-up", "result": {}})    


@app.post('/user/sign-up')
def register_request(request: Request, user: schemas.UserCreate = Depends(schemas.UserCreate.as_form), db: get_db = Depends()):
    result = {}

    try:
        user.validate_username()
        user.validate_password()

        created_user: schemas.User = UserService.register(db, user)
        UserService.add_to_role(db, created_user.id, 'User')
    except HTTPException as ex:
        result = ex.detail
    else:
        result = [{'title': 'Successfull registration', 'description': 'Created new user', 'type': 'success'}]


    return templates.TemplateResponse("user/sign-up/sign-up.html", {"request": request, "url_tab": "sign-up", "result": result})  


@app.post('/task')
def create_task(request: Request, task: schemas.TaskCreate = Depends(schemas.TaskCreate.as_form), db: get_db = Depends()):

    logined = request.session.get('token') is not None

    if not logined:
        return RedirectResponse(url="/user/sign-in", status_code=303)

    user = get_current_user(db, request.session['token'])
    TaskService.create_task(db, task, user.id)

    return RedirectResponse(url="/", status_code=303)