from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, Response
from accountservice import accountService

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
    account = accountService.get_by_name(user.email)
    if account is None:
        account = accountService.create(user.email)
    accountService.update_last_login(account)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie('access_token', accountService.create_access_token(user.email))
    return response


@app.middleware('http')
async def auth_middleware(request: Request, call_next):
    if os.environ.get('SKIP_AUTH') or request.url.path in ['/login', '/auth_callback','/openapi.json'] or request.url.path.startswith(
            '/docs'):
        return await call_next(request)

    user = accountService.get_by_token(request.cookies.get('access_token'))
    if user is None:
        return Response(status_code=401)
    return await call_next(request)


@app.get("/accounts")
def read_account(limit: int = 10, offset: int = 0):
    users = accountService.get_all(limit, offset)
    return users


@app.post("/accounts", status_code=201)
def create_account(request: requestmodels.CreateUserRequest):
    return accountService.create(request.name)


@app.get("/accounts/{account_id}")
def get_account(account_id: int):
    return accountService.get(account_id)


@app.delete("/accounts/{account_id}", status_code=202)
def delete_account(account_id: int):
    accountService.delete(account_id)


@app.put("/accounts/{account_id}", status_code=202)
def update_account(account_id: int, request: requestmodels.CreateUserRequest):
    accountService.update(account_id=account_id, name=request.name)
