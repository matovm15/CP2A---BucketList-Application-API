from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()


# User Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, onupdate=datetime.now())
    Buckets = db.relationship('Bucket', backref="user")

    def __repr__(self) -> str:
        return 'User>>> {self.username}'

# Bucket Database Model
class Bucket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bucket_name = db.Column(db.Text, nullable=False)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, onupdate=datetime.now())


    def __repr__(self) -> str:
        return 'Bucket >>> {self.bucket_name}'
