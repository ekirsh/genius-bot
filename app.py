import os
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import subprocess
import threading
from flask_cors import CORS

cred = credentials.Certificate('genius-bot-b8355-firebase-adminsdk-bookx-2d49ab4b27.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

app = Flask(__name__)
app.app_context().push()
CORS(app, resources={r"/*":{"origins":"*"}})

@app.route('/artist_data', methods=['POST'])
def artist_data():
    print('Received artist data request')
    data = request.get_json()
    artist_name = data.get('artistName')
    print('Artist name: {}'.format(artist_name))
    doc_ref = db.collection('artists').document(artist_name)
    doc = doc_ref.get()
    collab_ref = doc_ref.collection('collaborators')
    if doc.exists:
        print('Artist found in database, returning data...')
        print(doc.to_dict())
        return jsonify(doc.to_dict())
    else:
        print('Artist not found in database, scraping...')
        scraper_thread = threading.Thread(target=run_scraper, args=(artist_name,))
        scraper_thread.start()
        return jsonify({'message': 'Scraping artist...'})

@app.route('/')
def index():
    return 'Hello World'

def on_snapshot(doc_snapshot, changes, read_time):
    print('Received snapshot: {}'.format(doc_snapshot))

def run_scraper(artist):
    cmd = ['python3', 'newtrst.py', artist]
    subprocess.run(cmd)


if __name__ == '__main__':
    app.run(debug=True)