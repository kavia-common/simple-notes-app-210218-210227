from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# PUBLIC_INTERFACE
class NoteBase(BaseModel):
    """Base model for a Note, containing common fields."""

    title: str = Field(..., description="Title of the note", min_length=1)
    content: str = Field(..., description="Content/body of the note")


# PUBLIC_INTERFACE
class NoteCreate(NoteBase):
    """Model for creating a new note."""

    pass


# PUBLIC_INTERFACE
class NoteUpdate(BaseModel):
    """Model for updating an existing note. All fields are optional."""

    title: Optional[str] = Field(None, description="Updated title for the note", min_length=1)
    content: Optional[str] = Field(None, description="Updated content/body for the note")


# PUBLIC_INTERFACE
class Note(NoteBase):
    """Full Note model with server-managed fields."""

    id: str = Field(..., description="Unique identifier for the note")
    created_at: datetime = Field(..., description="Timestamp when the note was created")
    updated_at: datetime = Field(..., description="Timestamp when the note was last updated")
