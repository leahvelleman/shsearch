from flask_wtf import FlaskForm
from wtforms import StringField


class SearchForm(FlaskForm):
    search_string = StringField('search_string')
