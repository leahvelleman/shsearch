from flask import render_template, redirect, request, url_for
from app import app
from .forms import SearchForm
from .schema import schema, CREATOR, FULLTEXT
from whoosh.highlight import Highlighter, WholeFragmenter, ContextFragmenter
from whoosh.sorting import Count
from whoosh.query import Term, Or, And, Every, Phrase
from whoosh import index as _index


ix = _index.open_dir("indexdir")

cfh = Highlighter(fragmenter=ContextFragmenter())
wfh = Highlighter(fragmenter=WholeFragmenter())


@app.route('/', methods=('GET', 'POST'))
@app.route('/index.html', methods=('GET', 'POST'))
def index():
    return redirect(url_for(endpoint='search'))


@app.route('/about.html', methods=('GET', 'POST'))
def about():
    return render_template('about.html')


@app.route('/search', methods=('GET', 'POST'))
def search():
    arguments = request.args.to_dict(flat=False)

    facets = ["position", "meter", "key", "multiple_keys", "time"]
    everywhere = ["title", "lyrics", "composition_string", "poetry_string"]
    queries = [Every()]
    if 'q' in arguments:
        scope = arguments.pop('scope')[0] or 'all'
        value = arguments.pop('q')
        if scope == 'all':
            field = schema['lyrics']
            tokens = field.process_text(" ".join(value))
        elif type(schema[scope]) is FULLTEXT:
            field = schema[scope]
            tokens = field.process_text(" ".join(value))
        else:
            # do not stopword or tokenize, because we will store it as
            # a phrase. this isn't quite right, though, because we do
            # want to be lowercasing here, and possibly doing
            # normalizing of other kinds. perhaps the right way to do
            # this would be to put it through the appropriate field's
            # process_text but then smush it back together
            tokens = value
        if scope in arguments:
            arguments[scope] += tokens
        else:
            arguments[scope] = list(tokens)
        return redirect(url_for('search', **arguments))

    for keyword in arguments:
        if arguments[keyword]:
            if keyword == "all":
                terms = []
                for value in arguments[keyword]:
                    for subkeyword in everywhere:
                        terms.append(Term(subkeyword, value))
                # TODO: This is the wrong logic, because it makes all-fields
                # search terms optional.
                queries.append(Or(terms))
            else:
                terms = [Term(keyword, value) for value in arguments[keyword]]
                if type(schema[keyword]) is FULLTEXT:
                    queries.append(And(terms))
                else:
                    queries.append(Or(terms))
    query = And(queries)

    with ix.searcher() as s:
        songs = s.search(query, groupedby=facets, maptype=Count)
        everything = s.search(Every(), groupedby=facets)
        return render_template('search.html',
                               songs=songs,
                               everything=everything,
                               facets=facets,
                               arguments=arguments,
                               cfh=cfh, wfh=wfh)


def extend(dictionary, key, value):
    output = {k: [v for v in vs] for k, vs in dictionary.items()}
    if key in output:
        output[key].append(value)
    else:
        output[key] = [value]
    return output


def shrink(dictionary, key, value):
    output = {k: [v for v in vs] for k, vs in dictionary.items()}
    if key in output:
        output[key].remove(value)
    return output


app.jinja_env.globals.update(extend=extend)
app.jinja_env.globals.update(shrink=shrink)


@app.errorhandler(500)
def handle_500(e):
    return render_template('500.html', e=e), 500


@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html', e=e), 404
