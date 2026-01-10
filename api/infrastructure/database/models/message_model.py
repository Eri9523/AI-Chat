import mongoengine as mongo
from datetime import datetime

class MessageModel(mongo.Document):
    conversation_id = mongo.StringField(required=True)
    role = mongo.StringField(
        required=True,
        choices=['user', 'assistant', 'system']
    )

    content = mongo.StringField(required=True)
    status= mongo.StringField(
        required=True,
        choices=['pending', 'completed', 'error'],
        default='completed'
    )

    token_count=mongo.IntField()
    metadata = mongo.DictField(default=dict)
    error_message = mongo.StringField()
    created_at = mongo.DateTimeField(default=datetime.now)
    updated_at = mongo.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'messages',
        'indexes': [
            {'fields': ['conversation_id', 'created_at']},
            {'fields': ['role']},
        ],
        'ordering': ['created_at'],
        'auto_create_index': True
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(MessageModel, self).save(*args, **kwargs)