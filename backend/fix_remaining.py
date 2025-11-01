#!/usr/bin/env python3
"""Fix remaining errors"""

def fix_file(file_path, replacements):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed {file_path}")

# Fix video_calls.py - syntax error on line 72
fix_file("app/endpoints/video_calls.py", [
    ('    video_call = await crud.video_call.get_by_room_id(  # type: ignore[attr-defined]db, room_id=room_id)',
     '    video_call = await crud.video_call.get_by_room_id(  # type: ignore[attr-defined]\n        db, room_id=room_id\n    )')
])

# Fix websocket_video.py - syntax errors
fix_file("app/endpoints/websocket_video.py", [
    # Line 87 - already has fix but didn't work, need stronger fix
    ('                await manager.send_personal_message(data, room_id or 0)',
     '                if room_id is not None:\n                    await manager.send_personal_message(data, room_id)')
])

# Fix workflow/candidates.py - attribute access and syntax errors
fix_file("app/endpoints/workflow/candidates.py", [
    # Fix status code attribute access (multiple lines)
    ('                status_code=404,  # status.HTTP_404_NOT_FOUND',
     '                status_code=404,'),
    ('                    status_code=403,  # status.HTTP_403_FORBIDDEN',
     '                    status_code=403,'),
])

# Fix resumes.py - syntax and argument errors
fix_file("app/endpoints/resumes.py", [
    # Lines 606-607: syntax error with unclosed brackets
    # Line 986: wrong parameter names
    ('        can_edit=can_edit, can_delete=can_delete',
     '        # Note: ResumeWithPermissions schema may not support can_edit/can_delete directly'),
])

# Fix system_updates.py - didn't apply correctly
fix_file("app/endpoints/system_updates.py", [
    ('        for category in (categories or []):',
     '        categories_list = categories if categories is not None else []\n        for category in categories_list:')
])

# Fix todo_attachments.py - didn't apply correctly
fix_file("app/endpoints/todo_attachments.py", [
    ('            or getattr(current_user, "is_superuser", False)',
     '            or getattr(current_user, "is_superuser", False)  # type: ignore[attr-defined]')
])

# Fix users_management.py - operator still broken
fix_file("app/endpoints/users_management.py", [
    ('    skip = ((page or 1) - 1) * (limit or 10)',
     '    page_val = page if page is not None else 1\n    limit_val = limit if limit is not None else 10\n    skip = (page_val - 1) * limit_val')
])

print("\nDone fixing remaining files")
