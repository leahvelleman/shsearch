import re
import os
import os.path
import sqlite3
from whoosh.fields import Schema, TEXT, KEYWORD, NUMERIC
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import MultifieldParser
import whoosh.index as index

schema = Schema(title=TEXT(stored=True),
        meter_name=KEYWORD(commas=True, stored=True),
                song_text=TEXT(analyzer=StemmingAnalyzer(), stored=True),
                page=TEXT(stored=True),
                position=KEYWORD(stored=True))


if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

ix = index.create_in("indexdir", schema)
writer = ix.writer()
qp = MultifieldParser(["song_text", "title"], schema=schema)

source = sqlite3.connect("../shsearch-parsing/songs.db").cursor()

for row in source.execute("SELECT * FROM SONGS;"):
    page, position = re.match('([0-9]+)([tb]|$)', row[1]).group(1, 2)
    title = row[2]
    # ordinal = row[3]
    meter_name = row[4]
    song_text = row[6]
    writer.add_document(page=page, position=position, title=title,
                        meter_name=meter_name, song_text=song_text)
writer.commit()

