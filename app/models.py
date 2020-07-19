from app import app, db, whooshee

@whooshee.register_model('title', 'song_text')
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    page = db.Column(db.Integer)
    meter_name = db.Column(db.String)
    song_text = db.Column(db.String)
    position = db.Column(db.String)
    three_liner = db.Column(db.Integer)

    def __repr__(self):
        return '<Song {} {}>'.format(
                str(self.page) + str(self.position or ""),
                str(self.title))

