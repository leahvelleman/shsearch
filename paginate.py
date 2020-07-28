from app import db
from app.models import Song


def pair(in_list):
    return zip(*[in_list[i:] for i in (0, 1)])


songs = Song.query.all()
for thisone, nextone in pair(songs):
    if thisone.page != 'asdoif' and nextone.page != "asdoif":

        t = int(thisone.page)
        n = int(nextone.page)

        placenumber = (thisone.page % 2)*2
        placenumber += 1 if thisone.position == "b" else 0

        if thisone.position == "b":
            t += 0.5
        if nextone.position == "b":
            n += 0.5
        length = 2*(n-t)

        pageturn = placenumber + length > 4
        guttercross = ((placenumber + 2) % 4) + length > 4

        if guttercross:
            print(thisone.title, placenumber, 2*(n-t), guttercross)
