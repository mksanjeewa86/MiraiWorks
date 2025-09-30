# Router configuration
from fastapi import FastAPI

from app.endpoints import (
    assignment_workflow,
    auth,
    calendar,
    calendar_connections,
    companies,
    connection_invitations,
    dashboard,
    email_preview,
    exam,
    files,
    holidays,
    infrastructure,
    interviews,
    mbti,
    messages,
    notifications,
    positions,
    public,
    resumes,
    todo_attachments,
    todo_extensions,
    todos,
    user_connections,
    user_settings,
    users_management,
    video_calls,
    webhooks,
    websocket_video,
)
from app.endpoints.recruitment_workflow import processes, candidates


def include_routers(app: FastAPI) -> None:
    """Include all routers in the FastAPI app."""
    app.include_router(infrastructure.router, tags=["infrastructure"])
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

    # Messages system (unified messaging)
    app.include_router(
        messages.router, prefix="/api/messages", tags=["messages"]
    )
    app.include_router(
        notifications.router, prefix="/api/notifications", tags=["notifications"]
    )
    app.include_router(files.router, prefix="/api/files", tags=["files"])
    app.include_router(todos.router, prefix="/api/todos", tags=["todos"])
    app.include_router(assignment_workflow.router, prefix="/api/assignments", tags=["assignments"])
    app.include_router(todo_attachments.router, prefix="/api", tags=["todo-attachments"])
    app.include_router(todo_extensions.router, prefix="/api/todos", tags=["todo-extensions"])
    app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
    app.include_router(
        calendar_connections.router, prefix="/api/user", tags=["calendar-connections"]
    )
    app.include_router(holidays.router, prefix="/api/holidays", tags=["holidays"])
    app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])

    # Recruitment workflow endpoints
    app.include_router(processes.router, prefix="/api/recruitment-processes", tags=["recruitment-processes"])
    app.include_router(candidates.router, prefix="/api/recruitment-processes", tags=["recruitment-candidates"])
    app.include_router(video_calls.router, prefix="/api", tags=["video-calls"])
    app.include_router(websocket_video.router, tags=["websocket-video"])
    app.include_router(mbti.router, prefix="/api/mbti", tags=["mbti"])
    app.include_router(positions.router, prefix="/api/positions", tags=["positions"])
    app.include_router(exam.router, prefix="/api/exam", tags=["exam"])
    app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
    app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])
    app.include_router(user_settings.router, prefix="/api/user", tags=["user-settings"])
    app.include_router(user_connections.router, prefix="/api/user/connections", tags=["user-connections"])
    app.include_router(connection_invitations.router, prefix="/api/user/invitations", tags=["connection-invitations"])
    app.include_router(companies.router, prefix="/api/admin", tags=["companies"])
    app.include_router(
        users_management.router, prefix="/api/admin", tags=["users-management"]
    )
    app.include_router(public.router, prefix="/api/public", tags=["public"])

    # Development tools (only include in development)
    import os

    if os.getenv("ENVIRONMENT", "development").lower() in ["development", "local"]:
        app.include_router(email_preview.router, tags=["Email Preview"])
