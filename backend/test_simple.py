"""Simple test to validate messaging functionality without full DB setup"""
# -*- coding: utf-8 -*-

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_message_schema_import():
    """Test that we can import message schemas"""
    from app.schemas.direct_message import DirectMessageCreate, DirectMessageInfo
    from app.utils.constants import MessageType
    
    # Test creating a message schema
    message_data = DirectMessageCreate(
        recipient_id=1,
        content="Test message",
        type=MessageType.TEXT
    )
    
    assert message_data.content == "Test message"
    assert message_data.recipient_id == 1
    assert message_data.type == MessageType.TEXT
    print("OK Message schema import and creation test passed")

def test_message_constants():
    """Test message type constants"""
    from app.utils.constants import MessageType
    
    assert MessageType.TEXT.value == "text"
    assert MessageType.FILE.value == "file"
    print("OK Message constants test passed")

def test_services_import():
    """Test that services can be imported"""
    try:
        from app.services.direct_message_service import direct_message_service
        from app.services.notification_service import notification_service
        print("OK Services import test passed")
    except ImportError as e:
        print(f"FAIL Services import failed: {e}")
        raise

def test_models_import():
    """Test that models can be imported"""
    try:
        from app.models.direct_message import DirectMessage
        from app.models.user import User
        from app.models.notification import Notification
        print("OK Models import test passed")
    except ImportError as e:
        print(f"FAIL Models import failed: {e}")
        raise

if __name__ == "__main__":
    print("Running simple messaging tests...")
    
    test_message_schema_import()
    test_message_constants()
    test_services_import()
    test_models_import()
    
    print("All simple tests passed!")