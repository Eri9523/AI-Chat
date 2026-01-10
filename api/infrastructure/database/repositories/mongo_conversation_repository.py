from typing import List, Optional
from bson import ObjectId
from domain.entities.conversation import ConversationEntity, ConversationStatus
from domain.repositories.conversation_repository import IConversationRepository
from infrastructure.database.models.conversation_model import ConversationModel


class MongoConversationRepository(IConversationRepository):
    async def find_by_id(self, id: str) -> Optional[ConversationEntity]:
        conversation = ConversationModel.objects(id=id).first()
        if not conversation:
            return None
        return self._to_entity(conversation)
    
    async def find_by_user_id(
            self, 
            user_id: str, 
            limit: int = 20, 
            offset: int = 0
        ) -> List[ConversationEntity]:

        conversations = ConversationModel.objects(
            user_id=user_id,
            status__ne='deleted'
        ).skip(offset).limit(limit)

        return [self._to_entity(conv) for conv in conversations]
    
    async def create(self, conversation: ConversationEntity) -> ConversationEntity:
        new_conversation = ConversationModel(
            user_id=conversation.user_id,
            title=conversation.title,
            status=conversation.status.value,
            empathy_level=conversation.empathy_level,
            system_prompt=conversation.system_prompt,
            metadata=conversation.metadata
        )

        new_conversation.save()
        return self._to_entity(new_conversation)
    
    async def update(self, id: str, conversation_data: dict) -> Optional[ConversationEntity]:
        conversation = ConversationModel.objects(id=id).first()
        if not conversation:
            return None
        for key, value in conversation_data.items():
            if hasattr(conversation, key):
                setattr(conversation, key, value)
        conversation.save()
        return self._to_entity(conversation)
    
    async def delete(self, id: str) -> bool:
        result = ConversationModel.objects(id=id).update(status='deleted')
        return result > 0
    
    def _to_entity(self, conversation_doc) -> ConversationEntity:
        return ConversationEntity(
            id=str(conversation_doc.id),
            user_id=str(conversation_doc.user_id),
            title=conversation_doc.title,
            status=ConversationStatus(conversation_doc.status),
            empathy_level=conversation_doc.empathy_level,
            system_prompt=conversation_doc.system_prompt,
            created_at=conversation_doc.created_at,
            updated_at=conversation_doc.updated_at,
            metadata=conversation_doc.metadata
        )
