# 🏏 Fantasy Cricket Assistant with Live Stats and AI Suggestions

This is a Flask-based Fantasy Cricket Assistant web application that helps users build optimal fantasy teams using live cricket statistics, IPL data, and AI-generated suggestions via a local Ollama model.

---

## 🔧 Features

- 🌐 Live Cricket Stats (from Sportmonks API)
- 📊 IPL Match Scraping (from iplt20.com)
- 🤖 AI Assistant powered by local LLaMA model via Ollama
- 🧠 Custom training via Q&A pairs
- 📁 RESTful API endpoints
- 🖥️ HTML frontend (basic template included)

---

## 🚀 Getting Started

### 📦 Requirements

- Python 3.8+
- Flask, requests, bs4, flask_cors
- Ollama running locally with a LLaMA model (e.g., `llama3.2`)
- Sportmonks Cricket API key

### 🛠️ Installation

1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the server

```bash
python app.py
```

Open [http://localhost:5001](http://localhost:5001) in your browser.

---

## 📡 API Endpoints

- `GET /` — Home Page
- `POST /chat` — Ask a cricket-related question
- `POST /train` — Add custom Q&A training data
- `GET /stats` — Get latest cricket stats (Sportmonks)
- `GET /ipl` — Get live IPL match details (scraped)

---

## 📘 Example Prompt

```json
POST /chat
{
  "message": "Who should I pick as captain today?"
}
```

---

## 📂 File Structure

- `app.py` — Main Flask server
- `templates/index.html` — UI template
- `training_data.json` — Custom training data
- `static/` — Static files

---

## 🤖 AI Integration

This app uses a local Ollama server to query the `llama3.2` model for fantasy cricket suggestions based on:
- Live match data
- IPL schedule
- Custom training

Make sure your Ollama server is running at `http://localhost:11434`.

---

## 📬 Contact

Built by a cricket and AI enthusiast 🏏🤖