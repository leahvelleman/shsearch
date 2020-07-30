from collections import Counter
from flask import render_template, redirect, request, url_for
from app import app
from .forms import SearchForm
from .search import SearchTerms

from whoosh.fields import Schema, TEXT, KEYWORD, NUMERIC
from whoosh.query import Term, Or, And
from whoosh.analysis import StemmingAnalyzer
from whoosh.highlight import Highlighter, WholeFragmenter, ContextFragmenter
from whoosh.qparser import MultifieldParser
from whoosh.sorting import Count
from whoosh import index as _index

schema = Schema(title=TEXT(stored=True),
                meter_name=KEYWORD(commas=True, stored=True),
                song_text=TEXT(analyzer=StemmingAnalyzer(), stored=True),
                page=NUMERIC(stored=True),
                position=KEYWORD(stored=True))

ix = _index.open_dir("indexdir")
qp = MultifieldParser(["song_text", "title"], schema=schema)

cfh = Highlighter(fragmenter=ContextFragmenter())
wfh = Highlighter(fragmenter=WholeFragmenter())


@app.route('/', methods=('GET', 'POST'))
@app.route('/index.html', methods=('GET', 'POST'))
def index():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for(
                            endpoint='search',
                            song_text=form.search_string.data))
    return render_template('index.html', form=form)


@app.route('/about.html', methods=('GET', 'POST'))
def about():
    return render_template('about.html')


@app.route('/search', methods=('GET', 'POST'))
def search():
    query_terms = SearchTerms.from_query_string(request.query_string.decode('utf-8'))

    facets = ["meter_name", "page", "position"]
    with ix.searcher() as s:
        query_terms.clean_with(s)
        print(repr(query_terms.whoosh_query()))
        songs = s.search(query_terms.whoosh_query(),
                         groupedby=facets,
                         maptype=Count)
        print(songs)
        return render_template('search.html', songs=songs, facets=facets,
                search_terms=query_terms, cfh=cfh, wfh=wfh)


@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html', e=e), 500


@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html', e=e), 404
