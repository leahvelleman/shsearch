from app import app


@app.route('/')
@app.route('/index')
def index():
    return app.config['SQLALCHEMY_DATABASE_URI']
