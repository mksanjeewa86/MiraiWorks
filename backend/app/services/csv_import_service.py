import base64
import io
import logging
import secrets
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.role import Role, UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.utils.constants import UserRole as UserRoleEnum

logger = logging.getLogger(__name__)


class CSVImportService:
    def __init__(self):
        self.required_columns = ["email", "first_name", "last_name", "role"]
        self.optional_columns = ["phone", "company_id", "is_admin", "require_2fa"]

    def validate_csv_data(
        self, csv_content: str
    ) -> tuple[bool, list[str], pd.DataFrame]:
        """Validate CSV data and return errors if any."""
        errors = []
        df = None

        try:
            # Parse CSV
            df = pd.read_csv(io.StringIO(csv_content))

            # Check required columns
            missing_columns = [
                col for col in self.required_columns if col not in df.columns
            ]
            if missing_columns:
                errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                return False, errors, df

            # Validate data types and values
            for index, row in df.iterrows():
                row_errors = []

                # Email validation
                if pd.isna(row["email"]) or not str(row["email"]).strip():  # type: ignore[operator]
                    row_errors.append("Email is required")
                elif "@" not in str(row["email"]):
                    row_errors.append("Invalid email format")

                # Name validation
                if pd.isna(row["first_name"]) or not str(row["first_name"]).strip():  # type: ignore[operator]
                    row_errors.append("First name is required")
                if pd.isna(row["last_name"]) or not str(row["last_name"]).strip():  # type: ignore[operator]
                    row_errors.append("Last name is required")

                # Role validation
                if pd.isna(row["role"]) or not str(row["role"]).strip():  # type: ignore[operator]
                    row_errors.append("Role is required")
                else:
                    try:
                        UserRoleEnum(row["role"])
                    except ValueError:
                        valid_roles = [role.value for role in UserRoleEnum]
                        row_errors.append(
                            f"Invalid role. Must be one of: {', '.join(valid_roles)}"
                        )

                # Company ID validation (if provided)
                if "company_id" in df.columns and not pd.isna(row["company_id"]):  # type: ignore[operator]
                    try:
                        int(row["company_id"])
                    except (ValueError, TypeError):
                        row_errors.append("Company ID must be a number")

                # Boolean field validation
                for bool_field in ["is_admin", "require_2fa"]:
                    if bool_field in df.columns and not pd.isna(row[bool_field]):  # type: ignore[operator]
                        val = str(row[bool_field]).lower()
                        if val not in ["true", "false", "1", "0", "yes", "no"]:
                            row_errors.append(
                                f"{bool_field} must be true/false or 1/0 or yes/no"
                            )

                if row_errors:
                    errors.append(f"Row {int(index) + 2}: {'; '.join(row_errors)}")  # type: ignore[arg-type]

            return len(errors) == 0, errors, df

        except Exception as e:
            errors.append(f"Failed to parse CSV: {str(e)}")
            return False, errors, pd.DataFrame()

    def normalize_boolean(self, value: Any) -> bool:
        """Convert various boolean representations to bool."""
        if pd.isna(value):
            return False

        str_val = str(value).lower().strip()
        return str_val in ["true", "1", "yes", "y"]

    async def import_users_from_csv(
        self, db: AsyncSession, csv_content: str, default_company_id: int | None = None
    ) -> dict[str, Any]:
        """Import users from CSV data."""
        # Validate CSV
        is_valid, errors, df = self.validate_csv_data(csv_content)
        if not is_valid:
            return {
                "success": False,
                "created_users": 0,
                "failed_users": len(df) if df is not None else 0,
                "errors": errors,
                "created_user_ids": [],
            }

        created_users = []
        failed_users = []
        created_user_ids = []

        # Get existing roles
        role_result = await db.execute(select(Role))
        roles_map = {role.name: role for role in role_result.scalars().all()}

        # Process each row
        for index, row in df.iterrows():
            try:
                # Check if user already exists
                existing_user = await db.execute(
                    select(User).where(User.email == row["email"])
                )
                if existing_user.scalar_one_or_none():
                    failed_users.append(
                        f"Row {int(index) + 2}: User with email {row['email']} already exists"  # type: ignore[arg-type]
                    )
                    continue

                # Determine company_id
                company_id = None
                if "company_id" in df.columns and not pd.isna(row["company_id"]):  # type: ignore[operator]
                    company_id = int(row["company_id"])
                elif default_company_id:
                    company_id = default_company_id

                # Validate company exists if specified
                if company_id:
                    company_result = await db.execute(
                        select(Company).where(Company.id == company_id)
                    )
                    if not company_result.scalar_one_or_none():
                        failed_users.append(
                            f"Row {int(index) + 2}: Company ID {company_id} does not exist"  # type: ignore[arg-type]
                        )
                        continue

                # Generate temporary password
                temp_password = secrets.token_urlsafe(12)
                hashed_password = auth_service.get_password_hash(temp_password)

                # Create user
                user = User(
                    email=str(row["email"]).strip(),  # type: ignore[attr-defined]
                    first_name=str(row["first_name"]).strip(),  # type: ignore[attr-defined]
                    last_name=str(row["last_name"]).strip(),  # type: ignore[attr-defined]
                    phone=str(row.get("phone", "")).strip()  # type: ignore[attr-defined]
                    if not pd.isna(row.get("phone", ""))  # type: ignore[operator]
                    else None,
                    company_id=company_id,
                    hashed_password=hashed_password,
                    is_admin=self.normalize_boolean(row.get("is_admin", False)),
                    require_2fa=self.normalize_boolean(row.get("require_2fa", False)),
                    is_active=True,
                )

                db.add(user)
                await db.flush()  # Get user ID

                # Assign role
                role_name = str(row["role"]).strip()  # type: ignore[attr-defined]
                if role_name in roles_map:
                    user_role = UserRole(
                        user_id=user.id, role_id=roles_map[role_name].id
                    )
                    db.add(user_role)
                else:
                    # Create role if it doesn't exist (for custom roles)
                    new_role = Role(
                        name=role_name, description=f"Auto-created role: {role_name}"
                    )
                    db.add(new_role)
                    await db.flush()

                    user_role = UserRole(user_id=user.id, role_id=new_role.id)
                    db.add(user_role)
                    roles_map[role_name] = new_role

                created_users.append(
                    {
                        "email": user.email,
                        "temp_password": temp_password,
                        "name": user.full_name,
                    }
                )
                created_user_ids.append(user.id)

            except Exception as e:
                logger.error(f"Failed to create user from row {int(index) + 2}: {str(e)}")  # type: ignore[arg-type]
                failed_users.append(f"Row {int(index) + 2}: {str(e)}")  # type: ignore[arg-type]
                continue

        # Commit all changes
        if created_users:
            try:
                await db.commit()

                # Send activation emails
                for user_info in created_users:
                    try:
                        await email_service.send_user_activation(
                            user_info["email"],
                            user_info["name"],
                            user_info["temp_password"],
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to send activation email to {user_info['email']}: {str(e)}"
                        )
                        # Don't fail the import for email issues

            except Exception as e:
                await db.rollback()
                logger.error(f"Failed to commit user import: {str(e)}")
                return {
                    "success": False,
                    "created_users": 0,
                    "failed_users": len(df),
                    "errors": [f"Database error: {str(e)}"],
                    "created_user_ids": [],
                }

        return {
            "success": len(created_users) > 0,
            "created_users": len(created_users),
            "failed_users": len(failed_users),
            "errors": failed_users,
            "created_user_ids": created_user_ids,
        }

    async def process_csv_import(
        self, db: AsyncSession, csv_base64: str, default_company_id: int | None = None
    ) -> dict[str, Any]:
        """Process CSV import from base64 encoded data."""
        try:
            # Decode base64 CSV data
            csv_content = base64.b64decode(csv_base64).decode("utf-8")

            # Import users
            return await self.import_users_from_csv(db, csv_content, default_company_id)

        except Exception as e:
            logger.error(f"Failed to process CSV import: {str(e)}")
            return {
                "success": False,
                "created_users": 0,
                "failed_users": 0,
                "errors": [f"Failed to process CSV: {str(e)}"],
                "created_user_ids": [],
            }


# Global instance
csv_import_service = CSVImportService()
