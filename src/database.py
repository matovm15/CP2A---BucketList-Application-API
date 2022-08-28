from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime
db = SQLAlchemy()


# User Database Model
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, onupdate=datetime.now())
    Buckets = db.relationship('Bucket', backref="", passive_deletes=True)

    def __repr__(self) -> str:
        return 'User>>> {self.username}'

# BucketList Database Model
class Bucket(db.Model):
    bucket_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, onupdate=datetime.now())
    created_by = db.Column(db.Integer, db.ForeignKey('user.user_id',  ondelete='CASCADE'))
    items = db.relationship('Item', backref='bucket', passive_deletes=True)

    def serialize(self):
        return {
            'id': self.bucket_id,
            'name': self.name,
            'date_created': self.date_created,
            'date_modified': self.date_modified,
            'created_by': self.created_by
        }

# Bucketlist Items Database Model

class Item(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_modified = db.Column(db.DateTime, onupdate=datetime.now())
    done = db.Column(db.Boolean, default=False)
    bucket_id = db.Column(db.Integer, db.ForeignKey('bucket.bucket_id',ondelete='CASCADE'))

    def serailize(self):
        return {
            'item_id': self.item_id,
            'name': self.name,
            'date_created': self.date_created,
            'date_modified': self.date_modified,
            'created_by': self.created_by
        }

