#!/usr/bin/env python3
"""
Fix admin user password hashes in Docker MySQL database.
This script generates proper bcrypt hashes and updates the database.
"""

import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

import pymysql
from passlib.context import CryptContext

# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def main():
    """Fix admin user passwords."""
    # Database connection settings
    db_config = {
        "host": "localhost",
        "port": 3306,  # Default Docker MySQL port mapping
        "user": "hrms",
        "password": "hrms",
        "database": "miraiworks",
        "charset": "utf8mb4",
    }

    # Generate proper password hash for 'password'
    new_hash = hash_password("password")
    print(f"Generated password hash: {new_hash}")

    try:
        # Connect to database
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            # Get current hashes
            cursor.execute(
                "SELECT email, hashed_password FROM users WHERE email IN ('admin@example.com', 'admin@ccc.com')"
            )
            current_users = cursor.fetchall()

            print("Current password hashes:")
            for email, hash_value in current_users:
                print(f"  {email}: {hash_value[:50]}...")

            # Update password hashes
            cursor.execute(
                "UPDATE users SET hashed_password = %s WHERE email IN ('admin@example.com', 'admin@ccc.com')",
                (new_hash,),
            )

            # Commit changes
            connection.commit()

            # Verify changes
            cursor.execute(
                "SELECT email, LEFT(hashed_password, 50) as hash_preview FROM users WHERE email IN ('admin@example.com', 'admin@ccc.com')"
            )
            updated_users = cursor.fetchall()

            print(f"\nUpdated {cursor.rowcount} user password hashes:")
            for email, hash_preview in updated_users:
                print(f"  {email}: {hash_preview}...")

            print("\n✅ Password hashes fixed successfully!")
            print("✅ Both admin accounts now use password: 'password'")

    except Exception as e:
        print(f"❌ Error fixing passwords: {e}")
        return 1

    finally:
        if "connection" in locals():
            connection.close()

    return 0


if __name__ == "__main__":
    exit(main())
