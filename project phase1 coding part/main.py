from flask import Flask, render_template, request
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import json
import re

app = Flask(__name__)

# Initialize NLTK's Vader SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# YouTube API Configurations
YOUTUBE_API_KEY = "AIzaSyDno74tNiRW1bTo1SEEZMSMXANC9P2GRc"

# Route for the index page with the form to input the YouTube video link
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_link = request.form['video_link']
        sentiments, reactions = analyze_comments(video_link)
        return render_template('results.html', video_link=video_link, sentiments=sentiments, reactions=reactions)
    return render_template('index.html')

# Function to perform sentiment analysis on YouTube comments
def analyze_comments(video_link):
    video_id = extract_video_id(video_link)
    if not video_id:
        # Handle invalid YouTube links or display an error message
        return [], []

    comments = get_youtube_comments(video_id)
    sentiments = []
    reactions = []

    for comment in comments:
        sentiment_score = sia.polarity_scores(comment)
        sentiment = 'positive' if sentiment_score['compound'] >= 0 else 'negative' if sentiment_score['compound'] < 0 else 'neutral'
        sentiments.append((comment, sentiment))
        reactions.append(get_reaction(sentiment))

    return sentiments, reactions

# Function to fetch YouTube comments using the YouTube API
def get_youtube_comments(video_id):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={YOUTUBE_API_KEY}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in data['items']]
        return comments
    else:
        # Handle error when fetching comments
        return []

# Function to extract video id from the YouTube link
def extract_video_id(video_link):
    # Extract video id from the link using regular expression
    pattern = r"(?:youtu.be/|youtube.com/watch\?v=|youtube.com/embed/)([\w-]+)"
    match = re.search(pattern, video_link)

    if match:
        return match.group(1)
    else:
        return None

# Function to generate reactions (emojis) based on sentiment
def get_reaction(sentiment):
    # Implement your logic to generate reactions based on sentiment
    # For example, you can use emojis or predefined reactions for each sentiment
    return '😄' if sentiment == 'positive' else '😢' if sentiment == 'negative' else '😐'

if __name__ == '__main__':
    app.run(debug=True)
