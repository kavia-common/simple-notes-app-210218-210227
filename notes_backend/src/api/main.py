from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .repository import NotesRepository

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
