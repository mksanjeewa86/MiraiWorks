from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io
import os

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.crud.todo import todo as todo_crud
from app.crud.todo_attachment import todo_attachment
from app.schemas.todo_attachment import (
    TodoAttachmentInfo,
    TodoAttachmentList,
    FileUploadResponse,
    AttachmentStats,
    BulkDeleteRequest,
    BulkDeleteResponse,
    TodoAttachmentCreate
)
from app.services.file_storage_service import file_storage_service

router = APIRouter()


@router.post(
    "/todos/{todo_id}/attachments/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file attachment to todo"
)
async def upload_todo_attachment(
    todo_id: int,
    file: UploadFile = File(..., description="File to upload (max 25MB, any file type)"),
    description: Optional[str] = Form(None, description="Optional description for the file"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload a file attachment to a todo.
    
    - **todo_id**: ID of the todo to attach the file to
    - **file**: File to upload (maximum 25MB, any file type allowed)
    - **description**: Optional description for the file
    
    Returns information about the uploaded file.
    """
    # Verify todo exists and user has access
    db_todo = await todo_crud.get(db, id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Check if user owns the todo or created it
    if db_todo.owner_id != current_user.id and db_todo.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Save file using storage service
    try:
        file_info = await file_storage_service.save_file(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create attachment record in database
    attachment_data = TodoAttachmentCreate(
        todo_id=todo_id,
        original_filename=file_info["original_filename"],
        stored_filename=file_info["stored_filename"], 
        file_path=file_info["file_path"],
        file_size=file_info["file_size"],
        mime_type=file_info["mime_type"],
        file_extension=file_info.get("file_extension"),
        description=description,
        uploaded_by=current_user.id
    )
    
    db_attachment = await todo_attachment.create_attachment(
        db, attachment_data=attachment_data, uploader_id=current_user.id
    )
    
    return FileUploadResponse(
        message=f"File '{file.filename}' uploaded successfully",
        attachment=TodoAttachmentInfo.from_orm_with_computed(db_attachment)
    )


@router.get(
    "/todos/{todo_id}/attachments",
    response_model=TodoAttachmentList,
    summary="Get all attachments for a todo"
)
async def get_todo_attachments(
    todo_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all file attachments for a specific todo.
    
    - **todo_id**: ID of the todo
    - **skip**: Number of attachments to skip (for pagination)
    - **limit**: Maximum number of attachments to return
    """
    # Verify todo exists and user has access
    db_todo = await todo_crud.get(db, id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if db_todo.owner_id != current_user.id and db_todo.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get attachments
    attachments = await todo_attachment.get_todo_attachments(
        db, todo_id=todo_id, skip=skip, limit=limit
    )
    
    # Get summary stats
    summary = await todo_attachment.get_todo_attachment_summary(db, todo_id=todo_id)
    
    return TodoAttachmentList(
        attachments=[TodoAttachmentInfo.from_orm_with_computed(att) for att in attachments],
        total_count=summary["total_count"],
        total_size_mb=summary["total_size_mb"]
    )


@router.get(
    "/todos/{todo_id}/attachments/{attachment_id}",
    response_model=TodoAttachmentInfo,
    summary="Get attachment details"
)
async def get_attachment_details(
    todo_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get details of a specific attachment."""
    # Verify todo exists and user has access
    db_todo = await todo_crud.get(db, id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if db_todo.owner_id != current_user.id and db_todo.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get attachment
    db_attachment = await todo_attachment.get_attachment_by_id(
        db, attachment_id=attachment_id, todo_id=todo_id
    )
    if not db_attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    return TodoAttachmentInfo.from_orm_with_computed(db_attachment)


@router.get(
    "/todos/{todo_id}/attachments/{attachment_id}/download",
    summary="Download attachment file"
)
async def download_attachment(
    todo_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Download an attachment file."""
    # Verify todo exists and user has access
    db_todo = await todo_crud.get(db, id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if db_todo.owner_id != current_user.id and db_todo.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get attachment
    db_attachment = await todo_attachment.get_attachment_by_id(
        db, attachment_id=attachment_id, todo_id=todo_id
    )
    if not db_attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Check if file exists
    if not os.path.exists(db_attachment.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Return file response
    return FileResponse(
        path=db_attachment.file_path,
        filename=db_attachment.original_filename,
        media_type=db_attachment.mime_type
    )


@router.get(
    "/todos/{todo_id}/attachments/{attachment_id}/preview",
    summary="Preview attachment file"
)
async def preview_attachment(
    todo_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Preview an attachment file (for images and PDFs)."""
    # Verify todo exists and user has access
    db_todo = await todo_crud.get(db, id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if db_todo.owner_id != current_user.id and db_todo.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get attachment
    db_attachment = await todo_attachment.get_attachment_by_id(
        db, attachment_id=attachment_id, todo_id=todo_id
    )
    if not db_attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Check if preview is supported
    if not (db_attachment.is_image or db_attachment.mime_type == 'application/pdf'):
        raise HTTPException(status_code=400, detail="Preview not supported for this file type")
    
    # Check if file exists
    if not os.path.exists(db_attachment.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Return file for preview
    file_content = file_storage_service.get_file_content(db_attachment.file_path)
    if not file_content:
        raise HTTPException(status_code=404, detail="Could not read file")
    
    return StreamingResponse(
        io.BytesIO(file_content),
        media_type=db_attachment.mime_type,
        headers={"Content-Disposition": f"inline; filename={db_attachment.original_filename}"}
    )


@router.put(
    "/todos/{todo_id}/attachments/{attachment_id}",
    response_model=TodoAttachmentInfo,
    summary="Update attachment description"
)
async def update_attachment(
    todo_id: int,
    attachment_id: int,
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update attachment description."""
    # Verify todo exists and user has access
    db_todo = await todo_crud.get(db, id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if db_todo.owner_id != current_user.id and db_todo.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update attachment
    updated_attachment = await todo_attachment.update_attachment_description(
        db, attachment_id=attachment_id, description=description, user_id=current_user.id
    )
    if not updated_attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    return TodoAttachmentInfo.from_orm_with_computed(updated_attachment)


@router.delete(
    "/todos/{todo_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete attachment"
)
async def delete_attachment(
    todo_id: int,
    attachment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an attachment and its file."""
    # Verify todo exists and user has access
    db_todo = await todo_crud.get(db, id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if db_todo.owner_id != current_user.id and db_todo.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Delete attachment
    success = await todo_attachment.delete_attachment(
        db, attachment_id=attachment_id, todo_id=todo_id, cleanup_file=True
    )
    if not success:
        raise HTTPException(status_code=404, detail="Attachment not found")


@router.post(
    "/todos/{todo_id}/attachments/bulk-delete",
    response_model=BulkDeleteResponse,
    summary="Delete multiple attachments"
)
async def bulk_delete_attachments(
    todo_id: int,
    request: BulkDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete multiple attachments in one operation."""
    # Verify todo exists and user has access
    db_todo = await todo_crud.get(db, id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if db_todo.owner_id != current_user.id and db_todo.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Delete attachments
    result = await todo_attachment.delete_attachments_bulk(
        db, attachment_ids=request.attachment_ids, todo_id=todo_id, cleanup_files=True
    )
    
    return BulkDeleteResponse(
        message=f"Successfully deleted {result['deleted_count']} attachments",
        deleted_count=result["deleted_count"],
        failed_deletions=result["failed_deletions"]
    )


@router.get(
    "/todos/{todo_id}/attachments/stats",
    response_model=AttachmentStats,
    summary="Get attachment statistics"
)
async def get_attachment_stats(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get statistics about attachments for a todo."""
    # Verify todo exists and user has access
    db_todo = await todo_crud.get(db, id=todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    if db_todo.owner_id != current_user.id and db_todo.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get stats
    stats = await todo_attachment.get_attachment_stats(db, todo_id=todo_id)
    
    # Format file type counts
    file_type_counts = {}
    for category, data in stats["file_type_stats"].items():
        file_type_counts[category] = data["count"]
    
    return AttachmentStats(
        total_attachments=stats["total_count"],
        total_size_mb=stats["total_size_mb"],
        file_type_counts=file_type_counts,
        largest_file=TodoAttachmentInfo.from_orm_with_computed(stats["largest_file"]) if stats["largest_file"] else None,
        recent_attachments=[
            TodoAttachmentInfo.from_orm_with_computed(att) for att in stats["recent_attachments"]
        ]
    )


@router.get(
    "/attachments/my-uploads",
    response_model=List[TodoAttachmentInfo],
    summary="Get user's uploaded attachments"
)
async def get_my_uploads(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all attachments uploaded by the current user."""
    attachments = await todo_attachment.get_attachments_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    
    return [TodoAttachmentInfo.from_orm_with_computed(att) for att in attachments]


@router.post(
    "/admin/attachments/cleanup",
    summary="Cleanup orphaned attachments (Admin only)"
)
async def cleanup_orphaned_attachments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Clean up orphaned attachment records and files (Admin only)."""
    # Check if user is admin (you may need to adjust this based on your role system)
    if not current_user.is_superuser:  # Adjust based on your user model
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await todo_attachment.cleanup_orphaned_attachments(db)
    
    return {
        "message": "Cleanup completed",
        "deleted_db_records": result["deleted_db_records"],
        "orphaned_file_cleanup": result["file_cleanup"]
    }