#!/usr/bin/env python3
"""Initialize database with default roles and super admin."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.models.role import Role, UserRole
from app.services.auth_service import auth_service
from app.utils.constants import UserRole as UserRoleEnum


async def create_default_roles(db: AsyncSession):
    """Create default roles."""
    print("Creating default roles...")
    
    roles_created = 0
    for role_enum in UserRoleEnum:
        # Check if role exists
        result = await db.execute(
            select(Role).where(Role.name == role_enum.value)
        )
        existing_role = result.scalar_one_or_none()
        
        if not existing_role:
            role = Role(
                name=role_enum.value,
                description=f"Default {role_enum.value} role"
            )
            db.add(role)
            roles_created += 1
            print(f"  Created role: {role_enum.value}")
    
    await db.commit()
    print(f"Created {roles_created} new roles")


async def create_super_admin(db: AsyncSession, email: str, password: str, first_name: str, last_name: str):
    """Create super admin user."""
    print(f"Creating super admin user: {email}")
    
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        print(f"User {email} already exists")
        return existing_user
    
    # Create user
    hashed_password = auth_service.get_password_hash(password)
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=True,
        require_2fa=True,  # Super admin should have 2FA
        company_id=None  # Super admin doesn't belong to a company
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Assign super admin role
    role_result = await db.execute(
        select(Role).where(Role.name == UserRoleEnum.SUPER_ADMIN.value)
    )
    super_admin_role = role_result.scalar_one()
    
    user_role = UserRole(
        user_id=user.id,
        role_id=super_admin_role.id
    )
    
    db.add(user_role)
    await db.commit()
    
    print(f"Super admin user created successfully: {email}")
    return user


async def main():
    """Main initialization function."""
    print("Initializing MiraiWorks database...")
    
    try:
        # Initialize database tables
        await init_db()
        print("Database tables initialized")
        
        # Create default roles
        async with AsyncSessionLocal() as db:
            await create_default_roles(db)
        
        # Create super admin (you can customize these values)
        admin_email = input("Enter super admin email [admin@miraiworks.com]: ").strip()
        if not admin_email:
            admin_email = "admin@miraiworks.com"
        
        admin_password = input("Enter super admin password [password]: ").strip()
        if not admin_password:
            admin_password = "password"
        
        admin_first_name = input("Enter super admin first name [Super]: ").strip()
        if not admin_first_name:
            admin_first_name = "Super"
        
        admin_last_name = input("Enter super admin last name [Admin]: ").strip()
        if not admin_last_name:
            admin_last_name = "Admin"
        
        async with AsyncSessionLocal() as db:
            await create_super_admin(db, admin_email, admin_password, admin_first_name, admin_last_name)
        
        print("\n✅ Database initialization completed successfully!")
        print(f"   Super admin: {admin_email}")
        print("   You can now start the API server.")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())