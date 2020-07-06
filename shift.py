import re
import sqlite3
from app import db
from app.models import Song

source = sqlite3.connect("../shsearch-parsing/songs.db").cursor()
destination = sqlite3.connect("app.db").cursor()

for row in source.execute("SELECT * FROM SONGS;"):
    page, position = re.match('([0-9]+)([tb]|$)', row[1]).group(1, 2)
    title = row[2]
    #ordinal = row[3]
    meter_name = row[4]
    song_text = row[6]
    s = Song(title=title, page=page, meter_name=meter_name,
             song_text=song_text, position=position)
    db.session.add(s)
    db.session.commit()

