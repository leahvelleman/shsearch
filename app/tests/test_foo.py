from flask import url_for
from app.models import Song
from app import app


def test_root_route_is_200():
    with app.test_client() as client:
        rv = client.get('/')
        assert rv.status_code == 200


def test_search_key_errors_are_flashed():
    with app.test_client() as client:
        rv = client.get('/search?invalidkey=foo')
        assert rv.status_code == 200
        assert b'<ul class="AttributeError">' in rv.data
        assert b'invalidkey' in rv.data


def test_useful_404_page():
    with app.test_client() as client:
        rv = client.get('/invalidroutename')
        assert rv.status_code == 404
        assert rv.data
        assert url_for('index') in str(rv.data)


def test_song_get():
    s = Song.query.get(1)
    assert s
