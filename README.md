# Vibra 🎵🧠

[![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-%5E2.0-black?logo=flask)](https://flask.palletsprojects.com/)
[![MIT License](https://img.shields.io/github/license/Dimasnotofund/Vibra?color=green)](LICENSE)
[![GitHub Repo stars](https://img.shields.io/github/stars/Dimasnotofund/Vibra?style=social)](https://github.com/Dimasnotofund/Vibra/stargazers)

---

**Vibra** adalah aplikasi rekomendasi musik berbasis deteksi emosi dan genre favorit, terintegrasi dengan Spotify. Dengan **Vibra**, kamu bisa mendapatkan rekomendasi lagu yang sesuai dengan suasana hati secara real-time menggunakan AI Natural Language Processing dan Mood Chart Interaktif.

---

## 🚀 Demo & Tampilan

<!--
Ganti `static/demo.png` dengan path gambar hasil screenshot aplikasi.
-->
<p align="center">
  <img src="https://raw.githubusercontent.com/Dimasnotfound/Vibra/main/images/Screenshot_15.png" alt="Tampilan Halaman Utama Vibra" width="700"/>
</p>

<p align="center">
  <em>Tampilan utama aplikasi Vibra dengan fitur deteksi emosi dan mood chart.</em>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/Dimasnotfound/Vibra/main/images/Screenshot_16.png" alt="Chatbot Vibra" width="700"/>
</p>

---

## ✨ Fitur Utama

- 🔑 **Login dengan Spotify** (OAuth 2.0)
- 🤖 **Deteksi emosi otomatis** dari teks menggunakan model AI (IndoBERT)
- 🎨 **Mood Chart Interaktif** (drag emoji, genre otomatis ikut berubah)
- 🎵 **Rekomendasi lagu & genre** berdasarkan mood, emosi, dan preferensi genre
- 🏷️ **Pilih, tambah, dan hapus genre favorit** (multi-select, tidak dibatasi)
- ▶️ **Putar preview lagu langsung di aplikasi**
- 🔗 **Link langsung ke Spotify** jika preview lagu tidak tersedia

---

## 📦 Instalasi & Menjalankan

### 1. **Clone repo & install dependencies**

```bash
git clone https://github.com/Dimasnotofund/Vibra.git
cd Vibra
pip install -r requirements.txt
```

### 2. **Konfigurasi Environment**

Buat file `.env` lalu isi dengan:

```
SPOTIFY_CLIENT_ID=YOUR_CLIENT_ID
SPOTIFY_CLIENT_SECRET=YOUR_CLIENT_SECRET
FLASK_SECRET_KEY=random_secret_key
```

- Daftar aplikasi di [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- Ganti `YOUR_CLIENT_ID` dan `YOUR_CLIENT_SECRET` dengan milikmu.

### 3. **Jalankan Aplikasi**

```bash
python app.py
```

Buka browser ke [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📁 Struktur Folder

```
Vibra/
│
├── app.py                # Main Flask app
├── templates/            # HTML Jinja templates
│   ├── base.html
│   ├── index.html
│   ├── mood.html
│   └── songs.html
├── static/               # Gambar, logo, dan static files
│   ├── demo.png          # Ganti dengan screenshot aplikasi
│   └── vibra-illustration.png
├── emot-v3/              # Model BERT hasil fine-tune
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── tokenizer/
│   └── id2label.json
├── requirements.txt
└── README.md
```

---

## 💡 Cara Kerja Singkat

1. **Login via Spotify**  
2. **Masukkan atau pilih suasana hati**  
3. **AI menganalisis teks** → deteksi emosi → mood chart otomatis bergerak  
4. **Genre & rekomendasi lagu** berubah dinamis sesuai emosi/mood chart  
5. **Pilih genre favorit** (opsional, tidak dibatasi)  
6. **Klik "Temukan Lagu"** → Daftar lagu terbaik akan muncul  
7. **Putar preview lagu** langsung di aplikasi, atau klik ke Spotify jika ingin full

---

## 🔊 Preview Lagu

- **Hanya lagu dengan preview_url** yang dapat diputar langsung (30 detik, Spotify policy).
- Jika preview tidak tersedia, klik **"Dengarkan di Spotify"** untuk putar full.

---

## 🖼️ Ilustrasi Lain

Screenshot utama aplikasi:

- <p align="center">
  <img src="https://raw.githubusercontent.com/Dimasnotfound/Vibra/main/images/Screenshot_15.png" alt="Tampilan Halaman Utama Vibra" width="700"/>
</p>

Ilustrasi mood chart/fitur deteksi emosi :

- <p align="center">
  <img src="https://raw.githubusercontent.com/Dimasnotfound/Vibra/main/images/Screenshot_16.png" alt="Tampilan Halaman Utama Vibra" width="700"/>
</p>

Ilustrasi rekomendasi musik:

-<p align="center">
  <img src="https://raw.githubusercontent.com/Dimasnotfound/Vibra/main/images/Screenshot_18.png" alt="Tampilan Halaman Utama Vibra" width="700"/>
</p>

---

## 🤝 Kontribusi

Silakan open issue atau pull request untuk kontribusi, bug report, atau pengembangan fitur!

---

## 📜 Lisensi

MIT License.

---

## 👤 Kontak

- Dimas Notofund  
- [GitHub: Dimasnotofund](https://github.com/Dimasnotofund)
