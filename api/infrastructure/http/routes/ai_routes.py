from fastapi import APIRouter, Depends, UploadFile, File
from typing import List

from infrastructure.http.controllers.ai_controller import (
    ai_controller,
    CreateConversationRequest,
    SendMessageRequest,
    ConversationResponse,
    MessageResponse,
    DocumentResponse
)
from infrastructure.http.middlewares.auth_middleware import get_current_user


router = APIRouter()


# ==================== CONVERSATIONS ====================

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new conversation"""
    return await ai_controller.create_conversation(
        user_id=current_user["user_id"],
        request=request
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: dict = Depends(get_current_user)
):
    """Get all conversations for the current user"""
    return await ai_controller.get_conversations(
        user_id=current_user["user_id"]
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all messages for a conversation"""
    return await ai_controller.get_conversation_messages(
        user_id=current_user["user_id"],
        conversation_id=conversation_id
    )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a message to a conversation and get AI response"""
    return await ai_controller.send_message(
        user_id=current_user["user_id"],
        conversation_id=conversation_id,
        request=request
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a conversation and all its messages"""
    return await ai_controller.delete_conversation(
        user_id=current_user["user_id"],
        conversation_id=conversation_id
    )


# ==================== DOCUMENTS ====================

@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a document for RAG processing"""
    return await ai_controller.upload_document(
        user_id=current_user["user_id"],
        file=file
    )


@router.get("/documents", response_model=List[DocumentResponse])
async def get_documents(
    current_user: dict = Depends(get_current_user)
):
    """Get all documents for the current user"""
    return await ai_controller.get_documents(
        user_id=current_user["user_id"]
    )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a document and its vectors"""
    return await ai_controller.delete_document(
        user_id=current_user["user_id"],
        document_id=document_id
    )
