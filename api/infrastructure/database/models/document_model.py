import mongoengine as mongo
from datetime import datetime

class DocumentModel(mongo.Document):
    user_id = mongo.StringField(required=True)
    filename = mongo.StringField(required=True, max_length=255)
    content = mongo.StringField(required=True)
    document_type = mongo.StringField(
        required=True,
        choices=['text', 'pdf', 'markdown', 'html']
    )
    status = mongo.StringField(
        required=True,
        choices=['pending', 'processing', 'completed', 'error'],
        default='pending'
    )
    file_size = mongo.IntField(required=True)
    vector_ids = mongo.ListField(mongo.StringField())
    metadata = mongo.DictField(default=dict)
    error_message = mongo.StringField()
    created_at = mongo.DateTimeField(default=datetime.now)
    updated_at = mongo.DateTimeField(default=datetime.now)

    meta = {
        'collection': 'documents',
        'indexes': [
            {'fields': ['user_id', '-created_at']},
            {'fields': ['user_id', 'status']},
        ],
        'ordering': ['-created_at'],
        'auto_create_index': True
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(DocumentModel, self).save(*args, **kwargs)