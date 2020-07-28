from collections import defaultdict
from urllib.parse import parse_qs, urlencode
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, NUMERIC
from whoosh.highlight import Highlighter, WholeFragmenter, ContextFragmenter
from whoosh.qparser import MultifieldParser
from whoosh.query import Term, Or, And, Every
from whoosh.sorting import Count
from whoosh import index as _index

schema = Schema(title=TEXT(stored=True),
                meter_name=KEYWORD(commas=True, stored=True),
                song_text=TEXT(analyzer=StemmingAnalyzer(), stored=True),
                page=TEXT(stored=True),
                position=KEYWORD(stored=True))


class SearchTerms(defaultdict):

    disjunctive = {"meter_name", "position"}
    limited = {"meter_name", "position"}

    def __init__(self, query_string=None):
        super(SearchTerms, self).__init__(set)
        if query_string:
            items = parse_qs(query_string).items()
            for key, value in items:
                self[key].update(value)

    def __repr__(self):
        return urlencode(self, doseq=True)

    def handle_scope(self):
        # TODO: Make this feel less of a hack?
        if 'scope' in self and 'q' in self:
            k = self['scope'].pop()
            v = self['q']
            self[k].update(v)
            self['scope'] = set()
            self['q'] = set()

    def clean_with(self, s):
        # TODO: For text search fields, cull stopwords
        for k, vals in self.items():
            if k in self.limited:
                lexicon = list(s.field_terms(k))
                for v in list(vals):
                    if v not in lexicon:
                        self[k].discard(v)

    def plus(self, k, v):
        obj = SearchTerms(self.__repr__())
        obj[k].add(v)
        return obj

    def minus(self, k, v):
        obj = SearchTerms(self.__repr__())
        obj[k].discard(v)
        return obj

    def whoosh_query(self):
        queries = [Every()]  # An empty query gets everything
        for k in self:
            if self[k]:
                if k in self.disjunctive:
                    queries.append(Or([Term(k, v) for v in self[k]]))
                else:
                    queries.append(And([Term(k, v) for v in self[k]]))
        query = And(queries)
        return query


