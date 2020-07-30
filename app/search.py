from collections import defaultdict
from copy import deepcopy
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
    limited = {"meter_name", "position"}

    def __init__(self, **kwargs):
        super(SearchTerms, self).__init__(set)
        for k, v in kwargs.items():
            self[k] = set(v)

    def __repr__(self):
        print(self.items())
        return urlencode(self, doseq=True)

    def copy(self):
        return SearchTerms(**self)

    @classmethod
    def from_query_string(cls, query_string):
        obj = cls()
        if query_string:
            terms = parse_qs(query_string)
            print(terms)
            if 'q' in terms:
                scope = terms.get('scope')[0] or 'song_text'
                query_obj = qp.parse(" ".join(terms['q']))
                for token in query_obj.all_tokens():
                    obj[scope].add(token.text)
                terms.pop('q')
                terms.pop('scope')
            print(terms)
            for fieldname, value in terms.items():
                obj[fieldname].update(value)
        return obj

    def clean_with(self, s):
        # TODO: For text search fields, cull stopwords
        for k, vals in self.items():
            if k in self.limited:
                lexicon = list(s.field_terms(k))
                for v in list(vals):
                    if v not in lexicon:
                        self[k].discard(v)

    def plus(self, fieldname, value):
        obj = self.copy()
        obj[fieldname].add(value)
        return obj

    def minus(self, fieldname, value):
        obj = self.copy()
        obj[fieldname].discard(value)
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


