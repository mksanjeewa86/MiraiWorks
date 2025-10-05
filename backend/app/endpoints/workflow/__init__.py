# Workflow API Endpoints

from app.endpoints.workflow.candidates import router as candidates_router
from app.endpoints.workflow.nodes import router as nodes_router
from app.endpoints.workflow.workflows import router as workflows_router

__all__ = ["workflows_router", "nodes_router", "candidates_router"]
