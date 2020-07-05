from flask import render_template, redirect, request, url_for
from sqlalchemy import and_
from app import app
from app.models import Song
from .forms import SearchForm


@app.route('/songs')
def all_songs():
    songs = Song.query.all()
    return render_template('results.html', songs=songs)


@app.route('/', methods=('GET', 'POST'))
def search():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for(
                            endpoint='search_results',
                            query=form.search_string.data))
    return render_template('index.html', form=form)


@app.route('/search')
def search_results():
    form = SearchForm(request.form)

    filters = []
    for k in request.args:
        column = getattr(Song, k)
        comparison_string = '%{}%'.format(request.args[k])
        filters.append(column.like(comparison_string))
    songs = Song.query.filter(and_(*filters))

    return render_template('search.html', songs=songs, form=form)
