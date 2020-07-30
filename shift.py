import re
import os
import os.path
import sqlite3
from whoosh.qparser import MultifieldParser
import whoosh.index as index
from app.schema import schema


if not os.path.exists("indexdir"):
    os.mkdir("indexdir")

ix = index.create_in("indexdir", schema)
writer = ix.writer()
qp = MultifieldParser(["song_text", "title"], schema=schema)

source = sqlite3.connect("../shsearch-parsing/songs.db").cursor()

for row in source.execute("SELECT * FROM SONGS;"):
    print(row)
    kwargs = {}
    kwargs['page'], kwargs['position'] = \
        re.match('([0-9]+)([tb]|$)', row[1]).group(1, 2)
    kwargs['title'] = row[2]
    # ordinal = row[3]
    kwargs['meter_name'] = row[4]
    kwargs['song_text'] = row[6]
    kwargs['composer'] = row[8] + " " + row[9]
    kwargs['composition_year'] = row[10]
    writer.add_document(**kwargs)
writer.commit()
