from app import db
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

class Bucketlist(db.Model):
    """ Bucketlist database table structure"""

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
        """initialize with name."""
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