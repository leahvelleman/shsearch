from flask import render_template, redirect, request, url_for
from app import app
from app.models import Song
from .forms import SearchForm


@app.route('/')
@app.route('/index')
def index():
    return app.config['SQLALCHEMY_DATABASE_URI']


@app.route('/songs')
def all_songs():
    songs = Song.query.all()
    return render_template('results.html', songs=songs)


@app.route('/search', methods=('GET', 'POST'))
def search():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for(
                            endpoint='search_results',
                            query=form.search_string.data))
    return render_template('search.html', form=form)


@app.route('/search_results/<query>')
def search_results(query):
    songs = Song.query.filter_by(id = query).all()
    return render_template('results.html', songs=songs)
