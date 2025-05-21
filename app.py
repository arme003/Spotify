from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_restful import Api, Resource

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)

# Dummy user store
users = {'testuser': {'password': 'testpass'}}

# Dummy songs data
songs = [
    {'id': 1, 'title': 'Song One', 'artist': 'Artist A', 'url': '/static/audio/song1.mp3'},
    {'id': 2, 'title': 'Song Two', 'artist': 'Artist B', 'url': '/static/audio/song2.mp3'},
    {'id': 3, 'title': 'Song Three', 'artist': 'Artist C', 'url': '/static/audio/song3.mp3'},
]

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/')
@login_required
def index():
    playlist = session.get('playlist', [])
    return render_template('index.html', songs=songs, playlist=playlist)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

class SongList(Resource):
    @login_required
    def get(self):
        query = request.args.get('q', '').lower()
        if query:
            filtered = [s for s in songs if query in s['title'].lower() or query in s['artist'].lower()]
        else:
            filtered = songs
        return filtered

class Playlist(Resource):
    @login_required
    def get(self):
        return session.get('playlist', [])

    @login_required
    def post(self):
        song_id = request.json.get('song_id')
        if not song_id:
            return {'error': 'No song_id provided'}, 400
        playlist = session.get('playlist', [])
        # Avoid duplicates
        if song_id not in playlist:
            playlist.append(song_id)
            session['playlist'] = playlist
        return {'playlist': playlist}

    @login_required
    def delete(self):
        song_id = request.json.get('song_id')
        playlist = session.get('playlist', [])
        if song_id in playlist:
            playlist.remove(song_id)
            session['playlist'] = playlist
        return {'playlist': playlist}

api.add_resource(SongList, '/api/songs')
api.add_resource(Playlist, '/api/playlist')

if __name__ == '__main__':
    app.run(debug=True)
