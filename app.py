from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

CLIENT_ID = os.getenv("1395333135805452289")
CLIENT_SECRET = os.getenv("sRzTDEcRdvJQeFa4wDFB1WuwN0bPhDTc")
REDIRECT_URI = "https://discord.com/oauth2/authorize?client_id=1395333135805452289&response_type=code&redirect_uri=https%3A%2F%2Fdiscord-bot-ruma.onrender.com&scope=identify"  # Thay bằng domain deploy
DISCORD_API = "https://discord.com/api"


@app.get("/")
def home(request: Request):
    # Trang chính với nút Login
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
def login():
    # Redirect user tới trang Discord login
    oauth_url = (
        f"{DISCORD_API}/oauth2/authorize?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code&scope=identify"
    )
    return RedirectResponse(oauth_url)


@app.get("/callback")
def callback(request: Request, code: str):
    # Lấy access token từ code
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_res = requests.post(f"{DISCORD_API}/oauth2/token", data=data, headers=headers)
    token_json = token_res.json()
    access_token = token_json.get("access_token")

    # Lấy thông tin user từ Discord API
    user_res = requests.get(
        f"{DISCORD_API}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    user = user_res.json()

    # Logic kiểm tra điều kiện role (ví dụ: tất cả ai login đều verified)
    verified = True

    # Render trang kết quả
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": user.get("username"),
            "verified": verified,
        },
    )

