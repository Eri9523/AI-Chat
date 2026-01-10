from typing import Optional, AsyncGenerator
from domain.entities.conversation import ConversationEntity
from domain.entities.message import MessageEntity, MessageStatus
from domain.repositories.conversation_repository import IConversationRepository
from domain.repositories.message_repository import IMessageRepository
from domain.services.ai_service import IAIService
from domain.services.vector_service import IVectorService

class SendMessageDto:
    def __init__(
        self,
        user_id: str,
        conversation_id:str,
        content: str,
        use_rag: bool = False,
        stream: bool = False 
        ):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.content = content
        self.use_rag = use_rag
        self.stream = stream

class SendMessage:
    def __init__(
        self,
        conversation_repository: IConversationRepository,
        message_repository: IMessageRepository,
        ai_service: IAIService,
        vector_service: Optional[IVectorService] = None,
    ):
        self.conversation_repository=conversation_repository
        self.message_repository=message_repository
        self.ai_service=ai_service
        self.vector_service=vector_service

    async def execute(self, dto: SendMessageDto) -> dict | AsyncGenerator[dict, None]:
        conversation = await self.conversation_repository.find_by_id(dto.conversation_id)
        if not conversation or conversation.user_id != dto.user_id:
            raise Exception("Conversation not found or access denied")
        
        user_message = MessageEntity.create_user_message(
            conversation_id=dto.conversation_id,
            content=dto.content
        )

        saved_user_message = await self.message_repository.create(user_message)
        
        messages = await self.message_repository.find_by_conversation_id(dto.conversation_id)
        chat_history = self._prepare_chat_history(messages)

        context = ""
        if dto.use_rag and self.vector_service:
            context = await self._get_rag_context(dto.content, dto.user_id)

        system_prompt = self._prepare_system_prompt(conversation.system_prompt, context, conversation.empathy_level)

        assistant_message = MessageEntity.create_assistant_message(
            conversation_id=dto.conversation_id,
            content="",  # Será actualizado después de la respuesta de la IA
            status=MessageStatus.PENDING
        )

        saved_assistant_message = await self.message_repository.create(assistant_message)
        
        try:
            if dto.stream:
                return self._handle_streaming_response(
                    chat_history, system_prompt, saved_assistant_message
                )
            else:
                return await self._handle_regular_response(
                    chat_history, system_prompt, saved_assistant_message
                )
            
        except Exception as error:
            self.message_repository.update(
                saved_assistant_message.id,
                {
                    "status": MessageStatus.ERROR.value,
                    "error_message": str(error)
                }
            )
            raise

    async def _handle_regular_response(
        self,
        chat_history: list,
        system_prompt: Optional[str],
        assistant_message: MessageEntity
    ) -> dict:
        response = await self.ai_service.generate_chat_completion(
            messages=chat_history,
            system_prompt=system_prompt,
            stream=False
        )

        token_count = self.ai_service.count_tokens(response)
        updated_message = await self.message_repository.update(
            assistant_message.id, 
            {
                "content": response,
                "status": MessageStatus.COMPLETED.value,
                "token_count": token_count
            }
        )

        return {
            "message": {
                "id": updated_message.id,
                "content": response,
                "role": "assistant",
                "created_at": updated_message.created_at.isoformat(),
                "token_count": token_count
            }
        }


    async def _handle_streaming_response(
        self,
        chat_history: list,
        system_prompt: Optional[str],
        assistant_message: MessageEntity
    ) -> AsyncGenerator[dict, None]:
        full_response = ""

        async for chunk in self.ai_service.generate_chat_completion(
            messages=chat_history,
            system_prompt=system_prompt,
            stream=True
        ):
            full_response+= chunk

            # Streaming message flow. Content appears while receiving as flow. Looks cooler in UI
            yield {
                "type": "chunk",
                "content": chunk,
                "message_id": assistant_message.id
            }
        
        token_count = self.ai_service.count_tokens(full_response)
        await self.message_repository.update(
            assistant_message.id,
            {
                "content": full_response,
                "status": MessageStatus.COMPLETED.value,
                "token_count": token_count
            }
        )

        #This means message is completed (Check the type)
        yield {
            "type": "completed",
            "message_id": assistant_message.id,
            "token_count": token_count
        }


    async def _get_rag_context(self, query: str, user_id: str) -> str:
        if not self.vector_service:
            return ""
        
        similar_docs = await self.vector_service.search_similar(
            query=query,
            n_results=3,
            filters={"user_id": user_id}
        )

        context_parts = []
        for doc in similar_docs:
            context_parts.append(f"Document: {doc['metadata'].get('filename', 'Unknown')}\n {doc['document']}")
        
        #5 lines separation between rag contexts. For better legibility
        return "\n\n---\n\n".join(context_parts)
        

    def _prepare_system_prompt(self, base_prompt: Optional[str], rag_context: str, empathy_level: int) -> Optional[str]:
        if not base_prompt and not rag_context:
            return None
        
        prompt_parts = []
        
        # Add base prompt
        if base_prompt:
            prompt_parts.append(base_prompt)
        
        # Add empathy instructions
        empathy_instructions = self._get_empathy_instructions(empathy_level)
        prompt_parts.append(empathy_instructions)
        
        # Add RAG context
        if rag_context:
            prompt_parts.append(f"Relevant context from user documents: \n\n{rag_context}")

        return "\n\n".join(prompt_parts)
    
    def _get_empathy_instructions(self, empathy_level: int) -> str:
        if empathy_level <= 20:
            return "Respond in a direct and concise manner, focusing only on facts."
        elif empathy_level <= 40:
            return "Respond professionally but with some understanding of emotions."
        elif empathy_level <= 60:
            return "Show understanding and moderate empathy, acknowledging the user's emotions."
        elif empathy_level <= 80:
            return "Respond with high empathy, validating emotions and offering emotional support."
        else:
            return "Respond with maximum empathy and understanding, prioritizing the user's emotional well-being. Use a warm and supportive tone."
    

    def _prepare_chat_history(self, messages: list) -> list:
        chat_history = []
        for message in messages:
            if message.status == MessageStatus.COMPLETED:
                chat_history.append({
                    "role": message.role.value,
                    "content": message.content
                })
        return chat_history[-20:]  # Only last 20 messages
            
        