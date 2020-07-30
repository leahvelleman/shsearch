from collections import defaultdict
from copy import deepcopy
from flask import flash
from urllib.parse import parse_qs, urlencode
from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.query import Term, Or, And, Every
from whoosh.qparser import SimpleParser

text_analyzer = RegexTokenizer() | LowercaseFilter() | StopFilter()

schema = Schema(title=TEXT(analyzer=text_analyzer, stored=True),
                song_text=TEXT(analyzer=text_analyzer, stored=True),
                meter_name=KEYWORD(commas=True, stored=True),
                page=TEXT(stored=True),
                position=KEYWORD(stored=True))

qp = SimpleParser("song_text", schema=schema)


class SearchTerms(defaultdict):

    disjunctive = {"meter_name", "position"}
    everywhere = {"title", "song_text", "meter_name"}

    def __init__(self, **kwargs):
        super(SearchTerms, self).__init__(set)
        for k, v in kwargs.items():
            self[k] = set(v)

    def __repr__(self):
        return urlencode(self, doseq=True)

    def copy(self):
        return SearchTerms(**self)

    def clean_bad_keywords(self, s):
        # TODO: For text search fields, cull stopwords
        for fieldname, vals in list(self.items()):
            if type(schema[fieldname]) is KEYWORD:
                lexicon = list(s.field_terms(fieldname))
                for v in list(vals):
                    if v not in lexicon:
                        flash("no such {} as {}".format(fieldname, v), 'bad_keyword')
                        self[fieldname].discard(v)
                if not self[fieldname]:
                    self.pop(fieldname)
                        

    def plus(self, fieldname, value):
        obj = self.copy()
        obj[fieldname].add(value)
        return obj

    def minus(self, fieldname, value):
        obj = self.copy()
        obj[fieldname].discard(value)
        return obj

    @classmethod
    def from_query_string(cls, query_string):
        obj = cls()
        if query_string:
            terms = parse_qs(query_string)
            print(terms)
            if 'q' in terms:
                scope = terms.get('scope')[0] or 'all'
                value = terms['q']
                if scope == 'all':
                    # Handling items like "birdseye" will happen here
                    # Use the song text field's token parser
                    field = schema['song_text']
                    tokens = field.process_text(" ".join(value))
                elif type(schema[scope]) is TEXT:
                    field = schema[scope]
                    tokens = field.process_text(" ".join(value))
                else:
                    tokens = value
                obj[scope].update(tokens)
                terms.pop('q')
                terms.pop('scope')
            for fieldname, value in terms.items():
                obj[fieldname].update(value)
                print(obj)
        return obj

    def whoosh_query(self):
        queries = [Every()]  # An empty query gets everything
        for k in self:
            if self[k]:
                if k == 'all':
                    terms = []
                    for v in self[k]:
                        for subk in self.everywhere:
                            terms.append(Term(subk, v))
                    queries.append(Or(terms))
                elif k in self.disjunctive:
                    queries.append(Or([Term(k, v) for v in self[k]]))
                else:
                    queries.append(And([Term(k, v) for v in self[k]]))
        query = And(queries)
        return query


