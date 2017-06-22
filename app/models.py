from app import db
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

class Bucketlist(db.Model):
    """ Bucketlist database table structure"""

    # set the name of the table in plural
    __tablename__ = 'bucketlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    bucketlists = db.relationship('Items', backref='items')

    def __init__(self, name, user_id):
        """initialize with name, user_id."""

        self.name = name
        self.user = user_id


    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all_buckets_for_user(self, user_id):
        return Bucketlist.query.filter_by(user=user_id)

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucketlist {}>".format(self.name)

    class Items(db.Model):
        __tablename__ = 'items'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(255))
        date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
        date_modified = db.Column(
            db.DateTime, default=db.func.current_timestamp(),
            onupdate=db.func.current_timestamp())
        bucketlist = db.Column(db.Integer, db.ForeignKey('bucketlists.id'))

        def __init__(self, name, bucket_id):
            """initialize with name, bucket_id."""
            self.name = name
            self.bucketlist = bucket_id

        def save(self):
            db.session.add(self)
            db.session.commit()

        # get all itemes
        def get_all_items(self, bucketlist_id):
            return Items.query.filter_by(bucketlist=bucketlist_id)

        def update(self):
            db.session.commit()

        def delete(self):
            db.session.delete(self)
            db.session.commit()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    bucketlists = db.relationship('Bucketlist', backref='users')

    def __init__(self, username, email, password):
        """initialize with name."""
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode()

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>'.format(self.username)