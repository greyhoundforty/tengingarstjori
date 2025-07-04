#!/usr/bin/env python3
"""Debug script to test LocalForward validation behavior."""

from src.tengingarstjori.models import SSHConnection


def test_localforward_validation():
    """Test the new LocalForward validation logic."""
    print("Testing LocalForward validation...")

    # Test 1: Valid old format should be auto-corrected
    try:
        conn = SSHConnection(
            name="test1",
            host="example.com",
            user="testuser",
            local_forward="3306:localhost:3306",
        )
        print(f"✅ Auto-correction worked: '{conn.local_forward}'")
    except Exception as e:
        print(f"❌ Auto-correction failed: {e}")

    # Test 2: Invalid format should raise error
    try:
        conn = SSHConnection(
            name="test2",
            host="example.com",
            user="testuser",
            local_forward="invalid:format",
        )
        print(f"❌ Should have failed but got: '{conn.local_forward}'")
    except Exception as e:
        print(f"✅ Correctly caught invalid format: {e}")

    # Test 3: Already correct format should remain unchanged
    try:
        conn = SSHConnection(
            name="test3",
            host="example.com",
            user="testuser",
            local_forward="3306 localhost:3306",
        )
        print(f"✅ Correct format preserved: '{conn.local_forward}'")
    except Exception as e:
        print(f"❌ Valid format rejected: {e}")


if __name__ == "__main__":
    test_localforward_validation()
