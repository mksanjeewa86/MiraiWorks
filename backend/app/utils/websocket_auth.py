from urllib.parse import parse_qs

from fastapi import HTTPException, WebSocket, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth_service import AuthService


async def get_user_from_websocket(websocket: WebSocket, db: Session) -> User:
    """Extract and validate user from WebSocket connection"""

    # Get token from query parameters
    query_params = parse_qs(websocket.url.query)
    token = None

    if "token" in query_params:
        token = query_params["token"][0]

    if not token:
        # Try to get token from headers
        headers = dict(websocket.headers)
        auth_header = headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove 'Bearer ' prefix

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
        )

    # Validate token and get user
    auth_service = AuthService(db)
    try:
        user = auth_service.get_current_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )


def get_websocket_client_info(websocket: WebSocket) -> dict:
    """Extract client information from WebSocket connection"""

    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else 0

    headers = dict(websocket.headers)
    user_agent = headers.get("user-agent", "unknown")

    return {
        "host": client_host,
        "port": client_port,
        "user_agent": user_agent,
        "url": str(websocket.url),
    }
