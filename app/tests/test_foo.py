from app.models import Song
from app import app


def test_root_route_is_200():
    with app.test_client() as client:
        rv = client.get('/')
        assert rv.status_code == 200


def test_song_get():
    s = Song.query.get(1)
    assert s
