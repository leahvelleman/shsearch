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
                song_text=FULLTEXT(),
                meter_name=KEYWORD(commas=True, stored=True),
                page=TEXT(stored=True),
                position=KEYWORD(stored=True),
                composer=CREATOR(),
                composition_year=KEYWORD(stored=True))
