from app.models import Song


def test_song_get():
    s = Song.query.get(1)
    assert s
