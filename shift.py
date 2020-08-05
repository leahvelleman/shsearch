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

keys = set()

rows = list(source.execute("SELECT * FROM SONGS;"))
for row, nextrow in zip(rows, rows[1:]):
    kwargs = {}
    page, position = \
        re.match('([0-9]+)([tb]|$)', row[1]).group(1, 2)

    nextpage, nextposition = \
        re.match('([0-9]+)([tb]|$)', nextrow[1]).group(1, 2)

    kwargs['page'] = page
    kwargs['position'] = position

    pageno = int(page) + (0.5 if position == "b" else 0)
    nextpageno = int(nextpage) + (0.5 if nextposition == "b" else 0)

    kwargs['length'] = str(nextpageno - pageno)

    kwargs['title'] = row[2]
    # ordinal = row[3]
    kwargs['meter'] = row[4]
    kwargs['lyrics'] = row[6]
    kwargs['composer'] = row[8] + " " + row[9]
    kwargs['composition_year'] = row[10]
    if row[11] or row[12]:
        kwargs['composer'] += "," + row[11] + " " + row[12]
    if row[13]:
        kwargs['composition_year'] += "," + row[13]
    kwargs['composition_book'] = row[15]
    kwargs['poet'] = row[17] + " " + row[18]
    kwargs['poetry_year'] = row[19]
    if row[20] or row[21]:
        kwargs['poet'] += "," + row[20] + " " + row[21]
    if row[22]:
        kwargs['poetry_year'] += "," + row[22]
    kwargs['poetry_book'] = row[24]
    kwargs['key'] = row[26]
    kwargs['time'] = row[27]
    kwargs['composition_string'] = row[30]
    kwargs['poetry_string'] = row[31]
    if kwargs['composer'] and kwargs['composition_book']:
        print(list(zip(row, range(len(row)))))
        print(kwargs)
    writer.add_document(**kwargs)
writer.commit()
