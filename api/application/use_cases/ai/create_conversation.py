from typing import Optional
from domain.entities.conversation import ConversationEntity
from domain.repositories.conversation_repository import IConversationRepository


class CreateConversationDto:
    def __init__(
        self,
        user_id: str,
        title: str,
        system_prompt: Optional[str] = None,
        empathy_level: Optional[int] = 50,
        metadata: Optional[dict] = None
    ):
        self.user_id = user_id
        self.title = title
        self.system_prompt = system_prompt
        self.empathy_level = empathy_level or 50
        self.metadata = metadata


class CreateConversation:
    def __init__(self, conversation_repository: IConversationRepository):
        self.conversation_repository = conversation_repository

    async def execute(self, dto: CreateConversationDto) -> dict:
        conversation = ConversationEntity.create(
            user_id=dto.user_id,
            title=dto.title,
            system_prompt=dto.system_prompt,
            empathy_level=dto.empathy_level,
            metadata=dto.metadata
        )

        saved_conversation = await self.conversation_repository.create(conversation)

        return {
            "id": saved_conversation.id,
            "user_id": saved_conversation.user_id,
            "title": saved_conversation.title,
            "status": saved_conversation.status.value,
            "system_prompt": saved_conversation.system_prompt,
            "empathy_level": saved_conversation.empathy_level,
            "created_at": saved_conversation.created_at.isoformat(),
            "updated_at": saved_conversation.updated_at.isoformat(),
            "metadata": saved_conversation.metadata
        }
