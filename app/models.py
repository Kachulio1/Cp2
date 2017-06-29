# database object (db) from the main application module
from app import db
# Bcrypt for encrypting user password
from flask_bcrypt import Bcrypt

# an instantiate an instance of bcrypt
bcrypt = Bcrypt()


class Bucketlist(db.Model):
    """ Bucketlist database table structure"""

    # set the name of the table in plural
    __tablename__ = 'bucketlists'

    # database columns for table bucketlist
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    user = db.Column(db.Integer, db.ForeignKey('users.id'))
    items = db.relationship('Item', backref='items')

    def __init__(self, name, user_id):
        """initialize with name, user_id."""

        self.name = name
        self.user = user_id

    # save a bucket list to the database
    def save(self):
        db.session.add(self)
        db.session.commit()

    # gets all bucket lists for the user
    @staticmethod
    def get_all_buckets_for_user(user_id):
        return Bucketlist.query.filter_by(user=user_id).all()

    # saves the updated bucket list to the database
    def update(self):
        db.session.commit()

    # deletes a bucket list from the database
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Bucketlist {}>".format(self.name)


class Item(db.Model):
    # database table name
    __tablename__ = 'items'
    #
    # Database columns
    #
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    done = db.Column(db.Boolean,unique=False,default=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    bucketlist = db.Column(db.Integer, db.ForeignKey('bucketlists.id'))

    # end of database column

    def __init__(self, name, bucket_id):
        """initialize with name, bucket_id."""
        self.name = name
        self.bucketlist = bucket_id

    # save an item to the database
    def save(self):
        db.session.add(self)
        db.session.commit()

    # get all items
    @staticmethod
    def get_all_items(bucketlist_id):
        return Item.query.filter_by(bucketlist=bucketlist_id).all()

    # if the item is updated the update method is called and save's the updated item in the data base
    def update(self):
        db.session.commit()


    # delete an item from the db
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Item {}>".format(self.name)


# a User model
class User(db.Model):
    # database
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # User Name
    username = db.Column(db.String(80), nullable=False, unique=True)

    # Identification Data: email & password
    email = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    # Relationship between user and bucketlist
    bucketlists = db.relationship('Bucketlist', backref='users')

    # New instance instantiation procedure
    def __init__(self, username, email, password):
        """initialize with name."""
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode()

    # Checks if the passed password in the login post is the same with the user password in the database
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    # Save a user to the data base
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User {}>'.format(self.username)
