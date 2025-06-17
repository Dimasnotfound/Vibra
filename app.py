import os
from flask import Flask, render_template, redirect, url_for, session, request
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import json
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random
import math

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "changeme")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:5000/callback"

# Spotipy client (search lagu via genre)
client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

MODEL_PATH = "./emot-v3"
tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(MODEL_PATH)
with open(f"{MODEL_PATH}/id2label.json") as f:
    id2label = json.load(f)

# EMOTION_GENRE_MAP tetap seperti ini:
EMOTION_GENRE_MAP = {
    "anger": ["rock", "metal", "punk", "hardcore", "rap"],
    "fear": ["ambient", "soundtracks", "experimental", "darkwave"],
    "happy": ["pop", "dance", "edm", "funk", "reggae", "indie"],
    "love": ["soul", "r-n-b", "romantic", "ballad", "pop", "latin"],
    "neutral": ["jazz", "chill", "classical", "lo-fi", "folk"],
    "sad": ["ballad", "blues", "acoustic", "singer-songwriter", "indie", "classical"],
}

# Daftar genre manual awal (boleh dikurangi, nanti akan diupdate)
BASE_MANUAL_GENRES = [
    "pop",
    "rock",
    "jazz",
    "blues",
    "hip-hop",
    "indie",
    "dance",
    "edm",
    "metal",
    "funk",
    "acoustic",
    "r-n-b",
    "classical",
    "reggae",
    "folk",
    "country",
    "alternative",
    "lo-fi",
    "soul",
    "latin",
]

EMOTION_COORD = {
    "happy": {"x": 1, "y": 1},
    "anger": {"x": -1, "y": 1},
    "love": {"x": 1, "y": 0},
    "neutral": {"x": 0, "y": 0},
    "sad": {"x": -1, "y": -1},
}

# Lengkapi manual genre dengan semua genre unik dari EMOTION_GENRE_MAP
all_emotion_genres = set()
for genres in EMOTION_GENRE_MAP.values():
    all_emotion_genres.update(genres)
MANUAL_GENRES = list(
    dict.fromkeys(BASE_MANUAL_GENRES + list(all_emotion_genres))
)  # urutkan sesuai base, lalu tambahkan yg belum ada

# Setelah ini, MANUAL_GENRES sudah lengkap (unik, urutannya: base lalu sisanya di belakang)


def detect_emotion(text):
    model.eval()
    inputs = tokenizer(
        text, return_tensors="pt", truncation=True, padding=True, max_length=128
    )
    with torch.no_grad():
        outputs = model(**inputs)
        pred_id = torch.argmax(outputs.logits, dim=1).item()
    return id2label[str(pred_id)]


def suggest_genres_for_emotion(emotion, available_genres):
    preferred = EMOTION_GENRE_MAP.get(emotion, [])
    # Hanya masukkan genre yang ada di daftar manual
    valid = [g for g in preferred if g in available_genres]
    # Maksimal 3 genre untuk hasil, jika kurang dari 3 tambahkan dari manual (acak)
    if len(valid) < 3:
        extra = [g for g in available_genres if g not in valid]
        random.shuffle(extra)
        valid += extra[: 3 - len(valid)]
    return valid[:3]


# --------- Spotify OAuth & Refresh Token ---------
def refresh_spotify_token():
    refresh_token = session.get("spotify_token", {}).get("refresh_token")
    if not refresh_token:
        session.clear()
        return None
    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code != 200:
        print("Failed to refresh token:", response.status_code, response.text)
        session.clear()
        return None
    token_info = response.json()
    now = int(datetime.utcnow().timestamp())
    session["spotify_token"].update(
        {
            "access_token": token_info["access_token"],
            "expires_at": now + int(token_info.get("expires_in", 3600)),
            "timestamp": now,
            "expires_in": int(token_info.get("expires_in", 3600)),
        }
    )
    if "refresh_token" in token_info:
        session["spotify_token"]["refresh_token"] = token_info["refresh_token"]
    return session["spotify_token"]["access_token"]


def get_valid_spotify_token():
    token_info = session.get("spotify_token", {})
    token = token_info.get("access_token")
    expires_at = token_info.get("expires_at")
    now = int(datetime.utcnow().timestamp())
    if not token or not expires_at:
        return None
    if now > expires_at - 60:
        token = refresh_spotify_token()
    return token


def is_logged_in():
    token = get_valid_spotify_token()
    return bool(token)


@app.route("/")
def index():
    if is_logged_in():
        return redirect(url_for("mood"))
    return render_template("index.html")


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
    now = int(datetime.utcnow().timestamp())
    expires_in = int(token_info.get("expires_in", 3600))
    session["spotify_token"] = {
        "access_token": token_info["access_token"],
        "refresh_token": token_info.get("refresh_token"),
        "expires_at": now + expires_in,
        "timestamp": now,
        "expires_in": expires_in,
    }
    return redirect(url_for("mood"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/mood", methods=["GET", "POST"])
def mood():
    if not is_logged_in():
        return redirect(url_for("index"))
    detected_emotion = None
    nice_sentence = ""
    recommended_genres = []
    all_genres = MANUAL_GENRES
    mood_x, mood_y = 0, 0
    if detected_emotion in EMOTION_COORD:
        mood_x = EMOTION_COORD[detected_emotion]["x"]
        mood_y = EMOTION_COORD[detected_emotion]["y"]
    if request.method == "POST":
        text = request.form.get("mood_text") or ""
        detected_emotion = detect_emotion(text)
        recommended_genres = suggest_genres_for_emotion(detected_emotion, all_genres)
        mood_words = {
            "happy": "Kamu sedang merasa sangat bahagia!",
            "sad": "Kamu sedang merasa sedih, tidak apa-apa.",
            "anger": "Energi besar hari ini, yuk salurkan ke hal positif!",
            "love": "Hati kamu lagi hangat dan penuh cinta!",
            "neutral": "Kamu sedang tenang dan chill.",
            "fear": "Kamu sedang merasa cemas atau takut, coba dengarkan lagu yang menenangkan.",
        }
        nice_sentence = mood_words.get(detected_emotion, "Kamu sedang santai.")
    return render_template(
        "mood.html",
        detected_emotion=detected_emotion,
        nice_sentence=nice_sentence,
        recommended_genres=recommended_genres,
        all_genres=all_genres,
        mood_x=mood_x,
        mood_y=mood_y,
    )


@app.route("/discover", methods=["POST"])
def discover():
    genres = request.form.getlist("genres")
    emotion = request.form.get("emotion")
    valence = request.form.get("valence", type=float)
    energy = request.form.get("energy", type=float)

    # Filter hanya genre yang ada di list manual
    selected_genres = [g for g in genres if g in MANUAL_GENRES]
    if not selected_genres:
        # fallback: minimal 1 genre dari rekomendasi
        detected_emotion = emotion
        selected_genres = suggest_genres_for_emotion(detected_emotion, MANUAL_GENRES)

    total_genre = len(selected_genres)
    max_total = 30
    if total_genre == 0:
        return render_template(
            "songs.html",
            songs=[],
            genres="",
            emotion=emotion,
            valence=valence,
            energy=energy,
        )

    # Hitung alokasi lagu per genre
    base = max_total // total_genre
    sisa = max_total % total_genre
    allocation = [base] * total_genre
    for i in range(sisa):
        allocation[i] += 1  # Sisa dialokasikan ke genre paling awal

    songs = []
    for idx, genre in enumerate(selected_genres):
        n_lagu = allocation[idx]
        try:
            results = sp.search(q=f"genre:{genre}", type="track", limit=n_lagu)
            for track in results["tracks"]["items"]:
                songs.append(
                    {
                        "title": track["name"],
                        "artist": ", ".join([a["name"] for a in track["artists"]]),
                        "preview_url": track.get("preview_url")
                        or track["external_urls"]["spotify"],
                        "cover_url": track["album"]["images"][0]["url"]
                        if track["album"]["images"]
                        else "",
                        "genre": genre,
                    }
                )
        except Exception as e:
            print(f"Error fetching for genre {genre}: {e}")

    random.shuffle(songs)
    # Maksimal 30 lagu
    songs = songs[:max_total]

    return render_template(
        "songs.html",
        songs=songs,
        genres=", ".join(selected_genres),
        emotion=emotion,
        valence=valence,
        energy=energy,
        minValence=None,
        maxValence=None,
        minEnergy=None,
        maxEnergy=None,
    )


if __name__ == "__main__":
    app.run(debug=True)
