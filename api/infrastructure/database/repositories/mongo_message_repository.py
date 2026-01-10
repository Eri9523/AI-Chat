from typing import List, Optional
from bson import ObjectId
from domain.repositories.message_repository import IMessageRepository
from domain.entities.message import MessageEntity
from infrastructure.database.models.message_model import MessageModel

class MongoMessageRepository(IMessageRepository):
  async def create(self, message: MessageEntity) -> MessageEntity:
    message_model = MessageModel(
      conversation_id=message.conversation_id,
      role=message.role.value,
      content=message.content,
      created_at=message.created_at
    )

    message_model.save()
    message.id = str(message_model.id)
    return message
  
  async def find_by_id(self, message_id: str)  -> Optional[MessageEntity]:
    message_model = MessageModel.objects(id=message_id).first()
    if not message_model:
      return None
    return self._to_entity(message_model)
  
  async def find_by_conversation_id(self, conversation_id: str) -> List[MessageEntity]:
    messages = MessageModel.objects(conversation_id=conversation_id).order_by('+created_at')
    return [self._to_entity(m) for m in messages]

  async def update(self, id: str, message_data: dict) -> Optional[MessageEntity]:
    message = MessageModel.objects(id=id).first()
    if not message:
      return None
    
    from domain.entities.message import MessageRole, MessageStatus
    
    for key, value in message_data.items():
      if hasattr(message, key):
        # Convert enums to their string values
        if key == "role" and hasattr(value, 'value'):
          setattr(message, key, value.value)
        elif key == "status" and hasattr(value, 'value'):
          setattr(message, key, value.value)
        else:
          setattr(message, key, value)
    message.save()
    return self._to_entity(message)

  async def delete(self, id: str) -> bool:
    result = MessageModel.objects(id=id).delete()
    return result > 0

  async def delete_by_conversation_id(self, conversation_id: str) -> bool:
    result = MessageModel.objects(conversation_id=conversation_id).delete()
    return result > 0
  
  def _to_entity(self, model: MessageModel) -> MessageEntity:
    from domain.entities.message import MessageRole, MessageStatus
    return MessageEntity(
      id=str(model.id),
      conversation_id=str(model.conversation_id),
      role=MessageRole(model.role),
      content=model.content,
      status=MessageStatus(model.status) if hasattr(model, 'status') else MessageStatus.COMPLETED,
      created_at=model.created_at,
      updated_at=model.updated_at if hasattr(model, 'updated_at') else model.created_at
    )
  
