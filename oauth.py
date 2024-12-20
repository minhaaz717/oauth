import msal
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# Load Azure AD credentials from .env
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = os.getenv("AUTHORITY")
SCOPES = os.getenv("SCOPES").split(",")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Initialize MSAL (Microsoft Authentication Library)
msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)

# OAuth2PasswordBearer instance (for access tokens)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
async def login():
    auth_url = msal_app.get_authorization_request_url(SCOPES, redirect_uri=REDIRECT_URI)
    return RedirectResponse(auth_url)


@app.get("/login/callback")
async def login_callback(request: Request, code: str):
    result = msal_app.acquire_token_by_authorization_code(code, scopes=SCOPES, redirect_uri=REDIRECT_URI)

    if "access_token" in result:
        return {"access_token": result["access_token"]}
    else:
        raise HTTPException(status_code=400, detail="Authentication failed")


@app.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    # You would typically verify the token here
    return {"message": "This is a protected resource", "token": token}
