import mongoengine as mongo
from datetime import datetime

class ConversationModel(mongo.Document):
    user_id = mongo.StringField(required=True)
    title = mongo.StringField(required=True, max_length=200)
    status = mongo.StringField(
        required=True,
        choices=['active', 'archived', 'deleted'],
        default='active'
    )

    system_prompt=mongo.StringField()
    empathy_level = mongo.IntField(min_value=1, max_value=100, default=50)
    metadata=mongo.DictField(default=dict)
    created_at = mongo.DateTimeField(default=datetime.now)
    updated_at = mongo.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'conversations',
        'indexes': [
            {'fields': ['user_id', '-created_at']},
            {'fields': ['user_id', 'status']},
        ],
        'ordering': ['-created_at'],
        'auto_create_index': True
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(ConversationModel, self).save(*args, **kwargs)
