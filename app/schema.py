import re
from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter, IDTokenizer
from whoosh.fields import Schema, TEXT, KEYWORD
from whoosh.util.text import rcompile

text_analyzer = RegexTokenizer() | LowercaseFilter() | StopFilter()

creator_analyzer = RegexTokenizer() | LowercaseFilter()


class CREATOR(TEXT):
    def __init__(self):
        super().__init__(analyzer=creator_analyzer, stored=True)


class FULLTEXT(TEXT):
    def __init__(self):
        super().__init__(analyzer=text_analyzer, stored=True)


schema = Schema(title=FULLTEXT(),
                lyrics=FULLTEXT(),
                meter=KEYWORD(commas=True, stored=True),
                page=TEXT(stored=True),
                length=TEXT(),
                position=KEYWORD(stored=True),
                composer=CREATOR(),
                composition_year=KEYWORD(stored=True),
                composition_book=KEYWORD(stored=True),
                composition_string=FULLTEXT(),
                poet=CREATOR(),
                poetry_year=KEYWORD(stored=True),
                poetry_book=KEYWORD(stored=True),
                poetry_string=FULLTEXT(),
                key=KEYWORD(stored=True),
                time=KEYWORD(stored=True))
