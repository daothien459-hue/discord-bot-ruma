import os
from flask import Flask, redirect, request, session, url_for, render_template
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # Thay secret key thật khi deploy

# Discord OAuth Config
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "YOUR_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://127.0.0.1:5000/callback")
DISCORD_API_ENDPOINT = "https://discord.com/api"


@app.route("/")
def home():
    """Trang chính: nút đăng nhập"""
    return render_template("login.html", client_id=DISCORD_CLIENT_ID, redirect_uri=DISCORD_REDIRECT_URI)


@app.route("/callback")
def callback():
    """Nhận mã OAuth từ Discord, lấy access token & user info"""
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    token_res = requests.post(f"{DISCORD_API_ENDPOINT}/oauth2/token", data=data, headers=headers)
    token_json = token_res.json()
    access_token = token_json.get("access_token")

    if not access_token:
        return f"Failed to get access token: {token_json}", 400

    # Lấy thông tin người dùng
    user_res = requests.get(
        f"{DISCORD_API_ENDPOINT}/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    user_json = user_res.json()

    # Xử lý avatar URL
    avatar_id = user_json.get("avatar")
    if avatar_id:
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_json['id']}/{avatar_id}.png"
    else:
        avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"

    session["user"] = {
        "username": user_json.get("username", "Khách"),
        "avatar_url": avatar_url
    }

    return redirect(url_for("beach"))


@app.route('/beach')
def beach():
    """Trang nền bãi biển với user info"""
    user = session.get("user", {
        "username": "Khách",
        "avatar_url": "https://cdn.discordapp.com/embed/avatars/0.png"
    })
    return render_template('beach.html', username=user["username"], avatar_url=user["avatar_url"])


@app.route("/user-info")
def user_info():
    """API trả thông tin user cho front-end"""
    return session.get("user", {})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)


