from collections import defaultdict
from flask import flash
from urllib.parse import parse_qs, urlencode
from whoosh.fields import KEYWORD
from whoosh.query import Term, Or, And, Every, Phrase
from .schema import schema, CREATOR, FULLTEXT


class SearchTerms(defaultdict):

    disjunctive = {"meter_name", "position"}
    everywhere = {"title", "song_text", "meter_name", "composer"}

    def __init__(self, **kwargs):
        super(SearchTerms, self).__init__(set)
        for k, v in kwargs.items():
            self[k] = set(v)

    def __repr__(self):
        return urlencode(self, doseq=True)

    def copy(self):
        return SearchTerms(**self)

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
            if 'q' in terms:
                scope = terms.get('scope')[0] or 'all'
                value = terms['q']
                if scope == 'all':
                    # Handling items like "birdseye" will happen here
                    # Also, we use the song text field's token parser
                    field = schema['song_text']
                    tokens = field.process_text(" ".join(value))
                elif type(schema[scope]) is FULLTEXT:
                    field = schema[scope]
                    tokens = field.process_text(" ".join(value))
                else:
                    # do not stopword or tokenize, because we will store it as
                    # a phrase
                    tokens = value
                obj[scope].update(tokens)
                terms.pop('q')
                terms.pop('scope')
                print(terms)
            for fieldname, value in terms.items():
                obj[fieldname].update(value)
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
                elif k == 'composer':
                    queries.append(And([Phrase(k, v.split(" ")) for v in self[k]]))
                    print(queries)
                elif k in self.disjunctive:
                    queries.append(Or([Term(k, v) for v in self[k]]))
                else:
                    queries.append(And([Term(k, v) for v in self[k]]))
        query = And(queries)
        return query
