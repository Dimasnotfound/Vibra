import os
from flask import Flask, render_template, redirect, url_for, session, request
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv
import jwt
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "changeme")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:5000/callback"
JWT_SECRET = os.environ.get("FLASK_SECRET_KEY", "changeme")  # Untuk encode/decode JWT


def is_logged_in():
    """Cek session dan validasi JWT (kadaluarsa/token rusak)"""
    token = session.get("spotify_token", {}).get("access_token")
    id_token = session.get("spotify_token", {}).get("id_token")
    expires_at = session.get("spotify_token", {}).get("expires_at")

    # Spotify tidak memberi ID token, tapi punya expires_in & access_token
    if not token or not expires_at:
        return False

    # Cek expiry
    now = int(datetime.utcnow().timestamp())
    if now > expires_at:
        session.clear()
        return False

    # Bisa tambah pengecekan JWT kalau token berbasis JWT
    # try:
    #     jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    # except Exception:
    #     session.clear()
    #     return False

    return True


@app.route("/")
def index():
    # Jika sudah login, langsung redirect ke chatbot
    if is_logged_in():
        return redirect(url_for("chatbot"))
    return render_template("index.html")


@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if not is_logged_in():
        return redirect(url_for("index"))
    songs = []
    if request.method == "POST":
        mood = request.form.get("mood", "").lower()
        # TODO: Integrasi ke Spotify API untuk cari rekomendasi sesuai mood
        # Contoh dummy data:
        songs = [
            {
                "id": 1,
                "title": "All i want",
                "artist": "The Panturas",
                "preview_url": "#",
            },
            {"id": 2, "title": "Kuning", "artist": "Rumahsakit", "preview_url": "#"},
            {
                "id": 3,
                "title": "All the time",
                "artist": "The Sigit",
                "preview_url": "#",
            },
            {"id": 4, "title": "Merra", "artist": "Colordeo", "preview_url": "#"},
            {"id": 5, "title": "Did i try", "artist": "Enamore", "preview_url": "#"},
            {"id": 6, "title": "Autumn", "artist": "Murphy Radio", "preview_url": "#"},
        ]
    return render_template("chatbot.html", songs=songs)


@app.route("/login")
def login():
    scopes = "user-read-email user-read-private playlist-read-private"
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scopes,
        "show_dialog": "true",
    }
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return redirect(auth_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "No authorization code provided.", 400

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code != 200:
        return f"Failed to get token: {response.text}", 400

    token_info = response.json()
    # Hitung expiry absolut
    expires_in = token_info.get("expires_in", 3600)
    token_info["expires_at"] = int(datetime.utcnow().timestamp()) + int(expires_in)
    session["spotify_token"] = token_info

    return redirect(url_for("chatbot"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
