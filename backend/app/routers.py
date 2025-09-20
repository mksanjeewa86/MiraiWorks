# Router configuration
from fastapi import FastAPI

from app.endpoints import (
    auth,
    calendar,
    calendar_connections,
    companies,
    dashboard,
    direct_messages,
    email_preview,
    files,
    infrastructure,
    interviews,
    positions,
    messaging,
    notifications,
    todos,
    public,
    resumes,
    user_settings,
    users_management,
    webhooks,
)


def include_routers(app: FastAPI) -> None:
    """Include all routers in the FastAPI app."""
    app.include_router(infrastructure.router, tags=["infrastructure"])
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
    app.include_router(
        direct_messages.router, prefix="/api/direct-messages", tags=["direct-messages"]
    )
    app.include_router(messaging.router, prefix="/api/messaging", tags=["messaging"])
    app.include_router(
        notifications.router, prefix="/api/notifications", tags=["notifications"]
    )
    app.include_router(files.router, prefix="/api/files", tags=["files"])
    app.include_router(todos.router, prefix="/api/todos", tags=["todos"])
    app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"])
    app.include_router(
        calendar_connections.router, prefix="/api/user", tags=["calendar-connections"]
    )
    app.include_router(interviews.router, prefix="/api/interviews", tags=["interviews"])
    app.include_router(positions.router, prefix="/api/positions", tags=["positions"])
    app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
    app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])
    app.include_router(user_settings.router, prefix="/api/user", tags=["user-settings"])
    app.include_router(companies.router, prefix="/api/admin", tags=["companies"])
    app.include_router(
        users_management.router, prefix="/api/admin", tags=["users-management"]
    )
    app.include_router(public.router, prefix="/api/public", tags=["public"])

    # Development tools (only include in development)
    import os

    if os.getenv("ENVIRONMENT", "development").lower() in ["development", "local"]:
        app.include_router(email_preview.router, tags=["Email Preview"])
