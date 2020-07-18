from collections import Counter
from flask import render_template, redirect, request, url_for, flash
from sqlalchemy import and_, or_
from app import app, db
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
                            song_text=form.search_string.data))
    return render_template('index.html', form=form)


@app.route('/search', methods=('GET', 'POST'))
def search():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for(
                            endpoint='search',
                            song_text=form.search_string.data))
    args = request.args
    songs = search_songs(args)
    facetnames = ["meter_name", "page", "position"]
    facets = {f: Counter(getattr(s, f) for s in songs) for f in facetnames}
    meters = set(s.meter_name for s in songs)
    return render_template('search.html', songs=songs, form=form,
            args=args, facets=facets, request=request)


def search_songs(args):
    query_terms = []
    if args:
        for k in args:
            try:
                vs = args.getlist(k)
                query_terms.append(make_query_term(k, vs))
            except AttributeError:
                flash("Not a valid search term: {}".format(k))
    if query_terms:
        songs = Song.query.filter(and_(*query_terms))
    else:
        songs = Song.query.all()
    return songs


def make_query_term(k, vs):
    column = getattr(Song, k)
    if k == "song_text":
        return or_(*[column.like('%{}%'.format(v)) for v in vs])
    else:
        return or_(*[column == v for v in vs])


@app.route('/fuck')
def throw_an_error():
    # Some tests in test_foo.py currently depend on this. Remove it when we
    # are doing proper mocking or something
    assert False


@app.errorhandler(500)
def handle_500(e):
    # Currently unnecessary because we're not changing the DB in any routes,
    # but let's have it in there anyway
    db.session.rollback()
    return render_template('500.html', e=e), 500


@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html', e=e), 404
