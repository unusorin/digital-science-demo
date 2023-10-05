from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response
from userservice import userService

import requestmodels, sso
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI()


@app.get("/")
def healthcheck():
    return {"status": "Ok"}


@app.get("/login")
async def login():
    return await sso.google_sso.get_login_redirect(params={"prompt": "consent", "access_type": "offline"})


@app.get("/auth_callback")
async def auth_callback(request: Request):
    user = await sso.google_sso.verify_and_process(request)
    local_user = userService.get_by_name(user.email)
    if local_user is None:
        local_user = userService.create(user.email)
    userService.update_last_login(local_user)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie('access_token', userService.create_access_token(user.email))
    return response


@app.middleware('http')
async def auth_middleware(request: Request, call_next):
    if os.environ.get('SKIP_AUTH') or request.url.path in ['/login', '/auth_callback']:
        return await call_next(request)

    user = userService.get_by_token(request.cookies.get('access_token'))
    if user is None:
        return Response(status_code=401)
    return await call_next(request)


@app.get("/accounts")
def read_users(limit: int = 10, offset: int = 0):
    users = userService.get_all(limit, offset)
    return users


@app.post("/accounts", status_code=201)
def create_user(request: requestmodels.CreateUserRequest):
    return userService.create(request.name)


@app.get("/accounts/{user_id}")
def get_user(user_id: int):
    return userService.get(user_id)


@app.delete("/accounts/{user_id}", status_code=202)
def delete_user(user_id: int):
    userService.delete(user_id)


@app.put("/accounts/{user_id}", status_code=202)
def update_user(user_id: int, request: requestmodels.CreateUserRequest):
    userService.update(user_id=user_id, name=request.name)
