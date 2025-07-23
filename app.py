from flask import Flask, render_template, request, redirect, url_for, session
import requests
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session

# Hardcoded SerpAPI key
SERPAPI_KEY = "71569f56091bccb2dd4e85d9706836b151f50abf7378ceb0faeb36846c6ea4bb"

# Predefined topics
TOPICS = [
    "Python Basics",
    "Machine Learning",
    "Data Science",
    "Web Development",
    "Artificial Intelligence",
    "Deep Learning",
    "Flask Tutorial",
    "ReactJS Basics",
    "Natural Language Processing",
    "Data Structures"
]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/bot")
def bot():
    session.clear()  # Clear all session data
    return redirect(url_for('new_chat'))

@app.route("/bot/new")
def new_chat():
    session.clear()  # Clear all session data
    chat_id = str(uuid.uuid4())
    chat = {
        'id': chat_id,
        'created_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
        'history': []
    }
    session['chats'] = [chat]
    return redirect(url_for('chat', chat_id=chat_id))

@app.route("/bot/<chat_id>", methods=["GET", "POST"])
def chat(chat_id):
    session.clear()  # Clear all session data
    chat_id = str(uuid.uuid4())
    chat = {
        'id': chat_id,
        'created_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
        'history': []
    }
    session['chats'] = [chat]
    if request.method == "POST":
        topic = request.form.get("topic")
        if topic:
            chat['history'].append({"type": "user", "text": topic})
            params = {
                "engine": "youtube",
                "search_query": topic,
                "api_key": SERPAPI_KEY
            }
            response = requests.get("https://serpapi.com/search", params=params)
            videos = []
            if response.status_code == 200:
                data = response.json()
                results = data.get("video_results", [])[:5]
                for video in results:
                    video_link = video.get("link") or video.get("url")
                    video_id = None
                    if video_link:
                        if "v=" in video_link:
                            video_id = video_link.split("v=")[1].split("&")[0]
                        elif "youtu.be/" in video_link:
                            video_id = video_link.split("youtu.be/")[1].split("?")[0]
                        elif "/shorts/" in video_link:
                            video_id = video_link.split("/shorts/")[1].split("?")[0]
                    if video_id:
                        thumbnail = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                    else:
                        thumbnail = "https://via.placeholder.com/320x180?text=No+Thumbnail"
                    videos.append({
                        "title": video.get("title"),
                        "link": video_link,
                        "thumbnail": thumbnail
                    })
            if videos:
                chat['history'].append({"type": "bot", "text": f"Here are the top YouTube videos for '{topic}':"})
                chat['history'].append({"type": "videos", "videos": videos})
            else:
                chat['history'].append({"type": "bot", "text": f"Sorry, I couldn't find any videos for '{topic}'. Try another topic!"})
            session['chats'] = [chat]
    return render_template("bot.html", topics=TOPICS, chat_history=chat['history'], active_chat_id=chat_id)

if __name__ == "__main__":
    app.run(debug=True) 