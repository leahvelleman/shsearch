from flask_wtf import FlaskForm
from wtforms import StringField


class SearchForm(FlaskForm):
    song_text = StringField('song_text')
