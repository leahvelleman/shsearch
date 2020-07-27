from collections import Counter
from flask import render_template, redirect, request, url_for
from app import app
from .forms import SearchForm

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


@app.route('/search', methods=('GET', 'POST'))
def search():
    form = SearchForm(request.form)
    if form.validate_on_submit():
        return redirect(url_for(
                            endpoint='search',
                            song_text=form.search_string.data))
    args = request.args
    query_string = " ".join(args.getlist('q')) or ""
    queries = [qp.parse(query_string)]
    facets = ["meter_name", "page", "position"]
    for k in facets:
        if k in request.args:
            queries.append(Or([Term(k, v) for v in args.getlist(k)]))
    query = And(queries)

    with ix.searcher() as s:
        songs = s.search(query, groupedby=facets, maptype=Count)
        return render_template('search.html', songs=songs, wfh=wfh, cfh=cfh,
                               form=form, query=query_string, facets=facets,
                               request=request,
                               lexicon=ix.reader().lexicon("meter_name"))


@app.route('/fuck')
def throw_an_error():
    # Some tests in test_foo.py currently depend on this. Remove it when we
    # are doing proper mocking or something
    assert False


@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html', e=e), 500


@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html', e=e), 404
