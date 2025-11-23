from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .models import Note, NoteCreate, NoteUpdate


class NotesRepository:
    """A simple in-memory repository for managing notes.

    Thread-safe for basic CRUD operations using a re-entrant lock.
    """

    def __init__(self) -> None:
        # A dictionary keyed by note id
        self._notes: Dict[str, Note] = {}
        self._lock = threading.RLock()

    # PUBLIC_INTERFACE
    def list_notes(self) -> List[Note]:
        """Return all notes."""
        with self._lock:
            # Return a copy list to avoid exposing internal state
            return list(self._notes.values())

    # PUBLIC_INTERFACE
    def get_note(self, note_id: str) -> Optional[Note]:
        """Get a note by id, or None if not found."""
        with self._lock:
            return self._notes.get(note_id)

    # PUBLIC_INTERFACE
    def create_note(self, payload: NoteCreate) -> Note:
        """Create a new note from NoteCreate payload."""
        with self._lock:
            now = datetime.now(timezone.utc)
            note_id = str(uuid.uuid4())
            note = Note(
                id=note_id,
                title=payload.title,
                content=payload.content,
                created_at=now,
                updated_at=now,
            )
            self._notes[note_id] = note
            return note

    # PUBLIC_INTERFACE
    def update_note(self, note_id: str, payload: NoteUpdate) -> Optional[Note]:
        """Update an existing note. Returns updated note or None if not found."""
        with self._lock:
            existing = self._notes.get(note_id)
            if not existing:
                return None
            updated = existing.model_copy()
            if payload.title is not None:
                updated.title = payload.title
            if payload.content is not None:
                updated.content = payload.content
            updated.updated_at = datetime.now(timezone.utc)
            self._notes[note_id] = updated
            return updated

    # PUBLIC_INTERFACE
    def delete_note(self, note_id: str) -> bool:
        """Delete a note by id. Returns True if deleted, False if not found."""
        with self._lock:
            return self._notes.pop(note_id, None) is not None
