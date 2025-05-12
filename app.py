from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import os
import webbrowser
import threading
import subprocess
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS for all routes

OLLAMA_API_URL = "http://localhost:11434/api/generate"
TRAINING_FILE = "training_data.json"
SPORTMONKS_API_KEY = "LAvD0NILcvBUedqOXNUfP6LkVxUAfjS1G4BPfRT78QJlp0Br6th2dVZzZybQ"

# ================= Fetch Cricket Data from Sportmonks ===================
def get_live_cricket_stats():
    try:
        url = f"https://cricket.sportmonks.com/api/v2.0/fixtures?api_token={SPORTMONKS_API_KEY}&sort=-starting_at&include=localteam,visitorteam,scoreboards,runs"
        response = requests.get(url)
        data = response.json()

        if "data" not in data or len(data["data"]) == 0:
            return "No recent matches found."

        fixture = data["data"][0]  # Most recent match
        local_team = fixture["localteam"]["name"]
        visitor_team = fixture["visitorteam"]["name"]
        date = fixture["starting_at"]
        runs = fixture.get("runs", [])

        run_summary = ""
        for r in runs:
            team = local_team if r["team_id"] == fixture["localteam_id"] else visitor_team
            run_summary += f"{team}: {r['score']}/{r['wickets']} in {r['overs']} overs\n"

        return f"""
Match: {local_team} vs {visitor_team}
Date: {date}
Scores:
{run_summary}
"""
    except Exception as e:
        return f"Error fetching live stats: {e}"

# ================= Web Scraping for IPL Data ===================
def get_live_ipl_stats():
    try:
        # Replace with the actual URL of the website providing IPL data
        url = "https://www.example.com/ipl/matches"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Example: Extract match details
        match_details = []
        matches = soup.find_all('div', class_='match-card')  # Adjust the class based on the website's HTML structure
        for match in matches:
            team1 = match.find('div', class_='team-name').text.strip()
            team2 = match.find('div', class_='opponent-team-name').text.strip()
            venue = match.find('div', class_='venue').text.strip()
            date = match.find('div', class_='match-date').text.strip()
            format = match.find('div', class_='match-format').text.strip()

            match_details.append({
                "team1": team1,
                "team2": team2,
                "venue": venue,
                "date": date,
                "format": format
            })

        return match_details

    except Exception as e:
        return f"Error fetching live IPL stats: {e}"

# ================= Load Training Data (Custom Context) ===================
def load_training_context():
    if not os.path.exists(TRAINING_FILE):
        return ""
    with open(TRAINING_FILE, "r") as f:
        data = json.load(f)
        return "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in data])

# ================= Call Llama Model via Ollama ===================
def query_ollama(prompt: str, model: str = "llama3.2") -> str:
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={"model": model, "prompt": prompt, "stream": False}
        )
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        return f"Error: {e}"

# ================= Data Analysis and Visualization ===================
def analyze_and_visualize(data, prompt):
    try:
        # Example: Analyze the data based on the prompt and create a visualization
        teams = [match["team1"] for match in data]
        team_counts = {team: teams.count(team) for team in set(teams)}

        plt.figure(figsize=(10, 6))
        plt.bar(team_counts.keys(), team_counts.values())
        plt.xlabel('Teams')
        plt.ylabel('Number of Matches')
        plt.title('IPL Team Match Counts')

        # Save the plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # Encode the plot to base64 for sending in JSON
        plot_data = base64.b64encode(buf.read()).decode('utf-8')

        return plot_data

    except Exception as e:
        return f"Error analyzing and visualizing data: {e}"

# ================= API Routes ===================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "Message is required"}), 400

    cricket_stats = get_live_cricket_stats()
    training_context = load_training_context()

    prompt = f"""
You are a Fantasy Cricket Assistant. Use the stats and knowledge below to help the user build the best team.

Cricket Stats:
{cricket_stats}

Previous Training:
{training_context}

User: {user_input}
Assistant:"""

    response = query_ollama(prompt)
    return jsonify({"reply": response})

@app.route('/train', methods=['POST'])
def train():
    data = request.get_json()
    question = data.get("question", "").strip()
    answer = data.get("answer", "").strip()
    if not question or not answer:
        return jsonify({"error": "Both question and answer are required."}), 400

    if os.path.exists(TRAINING_FILE):
        with open(TRAINING_FILE, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.append({"question": question, "answer": answer})

    with open(TRAINING_FILE, "w") as f:
        json.dump(existing_data, f, indent=4)

    return jsonify({"message": "Training data added successfully."})

@app.route('/stats', methods=['GET'])
def stats():
    return jsonify({"stats": get_live_cricket_stats()})

@app.route('/ipl', methods=['GET'])
def ipl():
    ipl_data = get_live_ipl_stats()
    if isinstance(ipl_data, str):  # Check if an error occurred
        return jsonify({"error": ipl_data}), 500
    plot_data = analyze_and_visualize(ipl_data, "Show IPL team match counts")
    return jsonify({"ipl_stats": ipl_data, "plot": plot_data})

@app.route('/visualize', methods=['POST'])
def visualize():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    ipl_data = get_live_ipl_stats()
    if isinstance(ipl_data, str):  # Check if an error occurred
        return jsonify({"error": ipl_data}), 500
    plot_data = analyze_and_visualize(ipl_data, prompt)
    return jsonify({"plot": plot_data})

def open_browser():
    webbrowser.open_new('http://localhost:5001')

# ================= Run the App ===================
if __name__ == "__main__":
    # Open the browser
    threading.Thread(target=open_browser, daemon=True).start()

    # Run the Flask app
    app.run(debug=True, port=5001)
