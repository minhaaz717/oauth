import msal
import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
import base64
import hashlib
import os
import random
import string

# Load environment variables
load_dotenv()

# FastAPI app initialization
app = FastAPI()

# Setup templates for HTML rendering
templates = Jinja2Templates(directory="templates")

# Read environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = os.getenv("AUTHORITY")
SCOPES = os.getenv("SCOPES").split(",")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Initialize MSAL (Microsoft Authentication Library)
msal_app = msal.PublicClientApplication(
    CLIENT_ID, authority=AUTHORITY
)

# OAuth2PasswordBearer instance for access tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login():
    # Generate PKCE code challenge and code verifier
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    
    # Store the code_verifier in the session or use a temporary storage
    # In this example, we are not using sessions, but in production, it is needed.
    
    # Authorization URL with PKCE
    auth_url = msal_app.get_authorization_request_url(
        SCOPES,
        redirect_uri=REDIRECT_URI,
        code_challenge=code_challenge,
        code_challenge_method="S256"
    )
    
    return RedirectResponse(auth_url)

@app.get("/login/callback")
async def login_callback(request: Request, code: str):
    # Retrieve the code_verifier (in a real app, this would come from session/cookie)
    # For simplicity, we're just using the code_verifier generated during login.
    
    # Exchange the authorization code for an access token
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        code_verifier="your_code_verifier_here"  # Use the code verifier you stored earlier
    )

    if "access_token" in result:
        return {"access_token": result["access_token"]}
    else:
        raise HTTPException(status_code=400, detail="Authentication failed")

@app.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    # You can verify the token and fetch user info here
    return {"message": "This is a protected resource", "token": token}

# Utility functions to generate PKCE code verifier and challenge

def generate_code_verifier():
    # Generate a high-entropy random string for code verifier
    random_bytes = os.urandom(32)
    code_verifier = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip("=")
    return code_verifier

def generate_code_challenge(code_verifier: str):
    # Generate code challenge by hashing the code verifier with SHA256
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip("=")
    return code_challenge
