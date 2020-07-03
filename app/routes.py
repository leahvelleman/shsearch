from flask import render_template
from app import app
from app.models import Song


@app.route('/')
@app.route('/index')
def index():
    return app.config['SQLALCHEMY_DATABASE_URI']


@app.route('/songs')
def search():
    songs = Song.query.all()
    return render_template('results.html', songs=songs)
