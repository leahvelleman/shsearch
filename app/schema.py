from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter
from whoosh.fields import Schema, TEXT, KEYWORD, BOOLEAN

creator_analyzer = RegexTokenizer() | LowercaseFilter()
text_analyzer = RegexTokenizer() | LowercaseFilter() | StopFilter()
music_analyzer = RegexTokenizer() | LowercaseFilter()


class CREATOR(TEXT):
    def __init__(self):
        super().__init__(analyzer=creator_analyzer, stored=True)


class FULLTEXT(TEXT):
    def __init__(self):
        super().__init__(analyzer=text_analyzer, stored=True)


class MUSIC(TEXT):
    def __init__(self):
        super().__init__(analyzer=music_analyzer, phrase=True, chars=True, stored=True)


schema = Schema(title=FULLTEXT(),
                lyrics=FULLTEXT(),
                page=TEXT(stored=True),
                position=KEYWORD(stored=True),
                length=TEXT(),
                composer=CREATOR(),
                composition_year=KEYWORD(stored=True),
                composition_book=KEYWORD(stored=True),
                composition_string=FULLTEXT(),
                poet=CREATOR(),
                poetry_year=KEYWORD(stored=True),
                poetry_book=KEYWORD(stored=True),
                poetry_string=FULLTEXT(),
                key=KEYWORD(commas=True, stored=True),
                multiple_keys=BOOLEAN(),
                time=KEYWORD(commas=True, stored=True),
                meter=KEYWORD(commas=True, stored=True),
                treble=MUSIC(),
                alto=MUSIC(),
                tenor=MUSIC(),
                bass=MUSIC())
