from flask import render_template, redirect, request, url_for, flash
from sqlalchemy import and_
from app import app
from app.models import Song
from .forms import SearchForm


@app.route('/songs/')
def songs():
    form = SearchForm(request.form)
    songs = Song.query.all()
    return render_template('search.html', songs=songs, form=form)


@app.route('/', methods=('GET', 'POST'))
@app.route('/index.html', methods=('GET', 'POST'))
def index():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for(
                            endpoint='search',
                            query=form.search_string.data))
    return render_template('index.html', form=form)


@app.route('/search')
def search():
    form = SearchForm(request.form)

    filters = []
    for k in request.args:
        try:
            column = getattr(Song, k)
            comparison_string = '%{}%'.format(request.args[k])
            filters.append(column.like(comparison_string))
        except AttributeError:
            flash("Not a valid search term: {}".format(k))
    songs = Song.query.filter(and_(*filters))

    return render_template('search.html', songs=songs, form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
