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
    # TODO:
    # Handle empty string better
    # Redirect to resolve multiple
    # q strings
    query = " ".join(args.getlist('q')) or "God"

    facet_names = ["meter_name", "page", "position"]
    filters = {f: args.getlist(f) for f in facet_names}
    filter_query = get_filter_query(filters)

    songs = Song.query.whooshee_search(query).filter(filter_query)

    facets = {f: Counter(getattr(s, f) for s in songs) for f in facet_names}

    return render_template('search.html', songs=songs, form=form,
                           query=query, facets=facets, filters=filters,
                           request=request)


def get_filter_query(filters):
    query_terms = []
    for f in filters:
        vs = filters[f]
        query_terms.append(make_query_term(f, vs))
    return and_(*query_terms)


def make_query_term(k, vs):
    column = getattr(Song, k)
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
