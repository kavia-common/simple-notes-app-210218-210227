from typing import List

from fastapi import FastAPI, HTTPException, Path, status
from fastapi.middleware.cors import CORSMiddleware

from .repository import NotesRepository
from .models import Note, NoteCreate, NoteUpdate

openapi_tags = [
    {"name": "health", "description": "Service health and status"},
    {"name": "notes", "description": "Operations related to notes"},
]

app = FastAPI(
    title="Notes Backend API",
    description="API for managing notes in the Simple Notes App.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# Attach repository placeholder on app.state; real instance constructed at startup
app.state.notes_repo = None  # type: ignore[attr-defined]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set from env and restrict as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Create shared repository instance and store on app state."""
    app.state.notes_repo = NotesRepository()  # type: ignore[attr-defined]


@app.on_event("shutdown")
def on_shutdown() -> None:
    """Cleanup resources if needed."""
    # For in-memory repository there is no explicit cleanup needed.
    pass


@app.get("/", tags=["health"], summary="Health Check")
def health_check():
    """Health check endpoint to verify the API is running.

    Returns:
        dict: A message indicating the service is healthy.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get(
    "/notes",
    response_model=List[Note],
    tags=["notes"],
    summary="List notes",
    description="Retrieve a list of all notes.",
    responses={
        200: {
            "description": "List of notes returned successfully.",
        }
    },
)
def list_notes() -> List[Note]:
    """List all notes.

    Returns:
        List[Note]: Array of notes.
    """
    repo: NotesRepository = app.state.notes_repo  # type: ignore[assignment,attr-defined]
    return repo.list_notes()


# PUBLIC_INTERFACE
@app.post(
    "/notes",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
    tags=["notes"],
    summary="Create note",
    description="Create a new note with the provided title and content.",
    responses={
        201: {"description": "Note created successfully."},
        422: {"description": "Validation error on input."},
    },
)
def create_note(payload: NoteCreate) -> Note:
    """Create a new note.

    Parameters:
        payload (NoteCreate): Title and content for the new note.

    Returns:
        Note: The created note with server-generated fields.
    """
    repo: NotesRepository = app.state.notes_repo  # type: ignore[assignment,attr-defined]
    return repo.create_note(payload)


# PUBLIC_INTERFACE
@app.get(
    "/notes/{note_id}",
    response_model=Note,
    tags=["notes"],
    summary="Get note",
    description="Retrieve a specific note by its ID.",
    responses={
        200: {"description": "Note returned successfully."},
        404: {"description": "Note not found."},
    },
)
def get_note(
    note_id: str = Path(..., description="ID of the note to retrieve"),
) -> Note:
    """Get a specific note by ID.

    Parameters:
        note_id (str): The ID of the note.

    Returns:
        Note: The requested note if found.

    Raises:
        HTTPException: 404 if the note is not found.
    """
    repo: NotesRepository = app.state.notes_repo  # type: ignore[assignment,attr-defined]
    note = repo.get_note(note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


# PUBLIC_INTERFACE
@app.put(
    "/notes/{note_id}",
    response_model=Note,
    tags=["notes"],
    summary="Update note",
    description="Update the title and/or content of an existing note.",
    responses={
        200: {"description": "Note updated successfully."},
        404: {"description": "Note not found."},
        422: {"description": "Validation error on input."},
    },
)
def update_note(
    note_id: str = Path(..., description="ID of the note to update"),
    payload: NoteUpdate = ...,
) -> Note:
    """Update an existing note.

    Parameters:
        note_id (str): The ID of the note to update.
        payload (NoteUpdate): Fields to update (partial update allowed).

    Returns:
        Note: The updated note.

    Raises:
        HTTPException: 404 if the note is not found.
    """
    repo: NotesRepository = app.state.notes_repo  # type: ignore[assignment,attr-defined]
    updated = repo.update_note(note_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return updated


# PUBLIC_INTERFACE
@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["notes"],
    summary="Delete note",
    description="Delete a note by its ID.",
    responses={
        204: {"description": "Note deleted successfully."},
        404: {"description": "Note not found."},
    },
)
def delete_note(
    note_id: str = Path(..., description="ID of the note to delete"),
) -> None:
    """Delete a note by ID.

    Parameters:
        note_id (str): The ID of the note to delete.

    Returns:
        None

    Raises:
        HTTPException: 404 if the note is not found.
    """
    repo: NotesRepository = app.state.notes_repo  # type: ignore[assignment,attr-defined]
    deleted = repo.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    # 204 No Content, so return None
    return None
