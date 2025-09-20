import pytest
import asyncio


@pytest.mark.asyncio
async def test_simple_async():
    """Simple test to verify asyncio works."""
    await asyncio.sleep(0.001)
    assert True


def test_simple_sync():
    """Simple sync test."""
    assert True
