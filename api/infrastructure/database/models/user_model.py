import mongoengine as mongo
from datetime import datetime

class UserModel(mongo.Document):
    email = mongo.StringField(required=True, unique=True, lowercase=True, trim=True)
    name = mongo.StringField(required=True, trim=True)
    password = mongo.StringField(required=True)
    phone = mongo.StringField(trim=True)
    address=mongo.StringField()
    created_at = mongo.DateTimeField(default=datetime.now)
    updated_at = mongo.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'user',
        'indexes': [
            {'fields': ['email'], 'unique': True}
        ],
        'ordering': ['-created_at'],
        'auto_create_index': True
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(UserModel, self).save(*args, **kwargs)